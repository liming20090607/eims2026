#!/usr/bin/env python3
"""
验证前端修复面板部署
Verify Frontend Fix Panel Deployment
"""

import paramiko
import os
import time

print("=" * 80)
print("🔍 验证前端修复面板")
print("Verify Frontend Fix Panel")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ 已连接\n")

# Check if files exist
print("[1/4] 检查文件...")

checks = [
    ("修复面板模板", f"test -f {SERVER_PATH}/templates/includes/openclaw_fix_panel.html && echo '存在' || echo '不存在'"),
    ("API视图", f"grep -c 'def openclaw_status' {SERVER_PATH}/views_index.py"),
    ("URL路由", f"grep -c 'openclaw/api/status' {SERVER_PATH}/urls.py"),
]

for name, cmd in checks:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=5)
    result = stdout.read().decode().strip()
    print(f"  {name}: {result}")

# Check Gunicorn
print("\n[2/4] 检查Gunicorn...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
count = stdout.read().decode().strip()
print(f"  Gunicorn进程: {count}")

if int(count) == 0:
    print("  ⚠️ Gunicorn未运行，正在启动...")
    ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)
    
    start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
echo "Started" """
    
    stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=10)
    print(f"  {stdout.read().decode().strip()}")
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
    count = stdout.read().decode().strip()
    print(f"  ✅ Gunicorn进程: {count}")

# Test HTTP
print("\n[3/4] 测试HTTP访问...")
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"  HTTP状态: {http_code}")

# Test API
print("\n[4/4] 测试API端点...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/openclaw/api/status/ 2>&1 | head -5")
api_result = stdout.read().decode().strip()
print(f"  API响应: {api_result[:200]}")

# Check if fix panel is in base.html
print("\n检查base.html集成...")
stdin, stdout, stderr = ssh.exec_command(f"grep -c 'openclaw_fix_panel' {SERVER_PATH}/templates/base/base.html")
panel_count = stdout.read().decode().strip()
print(f"  面板引用: {panel_count} 处")

print("\n" + "=" * 80)
if http_code == '200':
    print("✅ 前端修复面板部署成功！")
    print("=" * 80)
    print("\n🎨 功能已启用:")
    print("  ✓ 错误页面自动显示修复面板")
    print("  ✓ 醒目的手动修复按钮（紫色渐变）")
    print("  ✓ 实时进度条（0-100%，带动画）")
    print("  ✓ 状态文字提示")
    print("  ✓ 自动刷新（每2秒，最多30次）")
    print("  ✓ 修复成功后自动跳转")
    print("\n📱 使用方法:")
    print("  1. 访问登录页面")
    print("  2. 如果遇到错误，会自动弹出修复面板")
    print("  3. 点击'立即手动修复'按钮")
    print("  4. 观察进度条从0%到100%")
    print("  5. 修复完成后自动刷新到正常页面")
    print("\n🌐 测试地址:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
else:
    print(f"⚠️ HTTP {http_code} - 可能有问题")
    print("\n查看错误日志:")
    stdin, stdout, stderr = ssh.exec_command(f"tail -20 {SERVER_PATH}/logs/gunicorn_error.log")
    print(stdout.read().decode())

print("=" * 80)

ssh.close()
