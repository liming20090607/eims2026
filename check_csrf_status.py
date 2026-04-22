#!/usr/bin/env python
"""
检查CSRF修复状态
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
print("🔍 CSRF修复状态检查")
print("="*70 + "\n")

# 1. 检查Gunicorn状态
print("[1] Gunicorn状态:")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
print(f"  工作进程数: {count}\n")

# 2. 检查CSRF配置
print("[2] CSRF配置:")
stdin, stdout, stderr = ssh.exec_command("grep -A 8 'CSRF_TRUSTED_ORIGINS' /var/www/eims/eims/settings.py | head -12")
csrf = stdout.read().decode().strip()
for line in csrf.split('\n'):
    print(f"  {line}")
print()

# 3. 测试登录页面
print("[3] 登录页面测试:")
tests = [
    ('GET /login/', 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/login/'),
    ('GET /login/ (完整响应头)', 'curl -s -I http://127.0.0.1:80/login/ | head -15'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"\n  {name}:")
    if 'http_code' in cmd:
        icon = "✅" if result in ['200', '302'] else "⚠️"
        print(f"  {icon} HTTP {result}")
    else:
        for line in result.split('\n')[:8]:
            print(f"    {line}")

# 4. 检查CSRF Cookie
print("\n[4] CSRF Cookie测试:")
test_cookie = """curl -s -c /tmp/csrf_test.txt http://127.0.0.1:80/login/ >/dev/null && grep csrftoken /tmp/csrf_test.txt"""
stdin, stdout, stderr = ssh.exec_command(test_cookie)
cookie = stdout.read().decode().strip()
if 'csrftoken' in cookie:
    print("  ✅ CSRF Cookie已生成")
    print(f"  {cookie[:80]}...")
else:
    print("  ❌ CSRF Cookie未生成")

ssh.close()

print("\n" + "="*70)
print("📋 修复建议:")
print("="*70)
print("\n1️⃣ 在浏览器中按 Ctrl+Shift+Delete")
print("   → 选择'全部时间'")
print("   → 勾选'Cookie和其他网站数据'")
print("   → 点击'清除数据'")
print("\n2️⃣ 或者直接按 Ctrl+F5 强制刷新")
print("\n3️⃣ 访问: http://www.xietongai.com.cn/login/")
print("\n4️⃣ 如果还有问题，尝试使用无痕模式 (Ctrl+Shift+N)")
print("="*70 + "\n")
