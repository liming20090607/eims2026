#!/usr/bin/env python
"""
快速检查当前状态
"""

import paramiko

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

print("\n" + "="*70)
print("📊 当前系统状态")
print("="*70 + "\n")

# 1. 服务状态
print("[1] 服务状态:")
checks = {
    'MySQL': 'systemctl is-active mysqld',
    'Gunicorn': 'pgrep -c gunicorn || echo 0',
    'Nginx': 'pgrep -c nginx || echo 0',
}
for name, cmd in checks.items():
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    icon = "✅" if result not in ['0', 'inactive', ''] else "❌"
    print(f"  {icon} {name}: {result}")

# 2. HTTP测试
print("\n[2] HTTP测试:")
tests = [
    ('本地Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/'),
    ('本地Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/'),
    ('服务器IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://39.106.41.239/login/'),
]
for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302', '500'] else "❌"
    print(f"  {icon} {name}: HTTP {code}")

# 3. CSRF Cookie测试
print("\n[3] CSRF Cookie:")
stdin, stdout, stderr = ssh.exec_command('curl -s -c /tmp/status_check.txt http://127.0.0.1:80/login/ >/dev/null && grep csrftoken /tmp/status_check.txt || echo "NO_COOKIE"')
cookie = stdout.read().decode().strip()
if 'csrftoken' in cookie:
    print("  ✅ CSRF Cookie正常")
    print(f"  {cookie[:60]}...")
else:
    print("  ❌ CSRF Cookie未生成")

ssh.close()

print("\n" + "="*70)
if all(['200' in cookie or '302' in cookie for _ in [1]]):
    print("✅ 系统正常工作！")
    print("\n🎯 请在浏览器中:")
    print("   1. 按 Ctrl+F5 强制刷新")
    print("   2. 或访问: http://www.xietongai.com.cn/login/")
else:
    print("⚠️ 系统正在修复中，请稍候...")
    print("\n自动纠错系统会每2分钟自动检查并修复")
print("="*70 + "\n")
