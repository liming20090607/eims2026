#!/usr/bin/env python
"""
彻底修复Gunicorn启动问题
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

print("\n" + "="*70)
print("🔧 彻底修复Gunicorn启动问题")
print("="*70 + "\n")

# 1. 检查settings.py完整性
print("[1] 检查settings.py...")
stdin, stdout, stderr = ssh.exec_command("wc -l /var/www/eims/eims/settings.py && grep -c 'DATABASES' /var/www/eims/eims/settings.py && grep -c 'CSRF_TRUSTED_ORIGINS' /var/www/eims/eims/settings.py")
result = stdout.read().decode().strip()
print(f"  {result}")

# 2. 检查Python导入错误
print("\n[2] 测试Django导入...")
test_import = """cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import sys, os
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
try:
    import django
    django.setup()
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(test_import)
import_result = stdout.read().decode().strip()
print(f"  {import_result}")

if 'SUCCESS' not in import_result:
    print("\n  ❌ Django无法启动，检查错误详情:")
    # 获取完整错误堆栈
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && /var/www/eims/venv/bin/python -c \"import sys, os; sys.path.insert(0, '/var/www/eims'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings'); import django; django.setup()\" 2>&1")
    full_error = stdout.read().decode().strip()
    for line in full_error.split('\n')[-10:]:
        print(f"    {line}")
    
    # 3. 如果settings.py有问题，重新上传
    print("\n[3] 修复settings.py...")
    print("  正在从本地上传正确的settings.py...")
    
    # 读取本地settings.py
    local_path = 'e:\\EIMS2026\\settings.py'
    try:
        with open(local_path, 'r', encoding='utf-8') as f:
            settings_content = f.read()
        
        # 确保CSRF配置正确
        if 'CSRF_TRUSTED_ORIGINS' not in settings_content:
            print("  ⚠️  本地settings.py缺少CSRF配置，添加中...")
            csrf_addition = """
CSRF_TRUSTED_ORIGINS = [
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'http://39.106.41.239',
    'http://localhost',
    'http://127.0.0.1',
]
"""
            settings_content += csrf_addition
        
        # 上传到服务器
        stdin, stdout, stderr = ssh.exec_command(
            f'cat > /var/www/eims/eims/settings.py << SETTINGS_EOF\n{settings_content}\nSETTINGS_EOF',
            timeout=30
        )
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command("wc -l /var/www/eims/eims/settings.py")
        lines = stdout.read().decode().strip()
        print(f"  ✅ settings.py已上传: {lines} 行")
        
    except Exception as e:
        print(f"  ❌ 上传失败: {e}")

# 4. 清除所有Gunicorn进程
print("\n[4] 清理旧进程...")
ssh.exec_command('pkill -9 gunicorn || true')
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
print(f"  Gunicorn进程数: {count}")

# 5. 尝试启动Gunicorn
print("\n[5] 启动Gunicorn...")
cmd = 'cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 120 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log >/dev/null 2>&1 &'
stdin, stdout, stderr = ssh.exec_command(cmd)
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
print(f"  Gunicorn工作进程: {count}")

# 6. 测试HTTP
print("\n[6] HTTP测试...")
tests = [
    ('本地8000', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('本地80', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
]
for name, test_cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302'] else "❌"
    print(f"  {icon} {name}: HTTP {code}")

# 7. 检查最新错误日志
if count == '0':
    print("\n[7] 最新错误日志:")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn_error.log')
    errors = stdout.read().decode().strip()
    for line in errors.split('\n')[-15:]:
        print(f"  {line}")

ssh.close()

print("\n" + "="*70)
if count != '0':
    print("✅ Gunicorn已成功启动！")
    print("\n现在请在浏览器中:")
    print("  1. 按 Ctrl+F5 强制刷新")
    print("  2. 访问: http://www.xietongai.com.cn/login/")
else:
    print("❌ Gunicorn仍然无法启动")
    print("\n需要进一步检查settings.py和依赖")
print("="*70 + "\n")
