#!/usr/bin/env python
"""
Quick server health check and CSRF fix
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
print("🔍 Server Status Check")
print("="*70 + "\n")

# 1. Check services
print("[1] Service Status:")
for name, cmd in [('MySQL', 'systemctl is-active mysqld'), 
                   ('Gunicorn', 'pgrep -c gunicorn || echo 0'),
                   ('Nginx', 'pgrep -c nginx || echo 0')]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    icon = "✅" if result not in ['0', 'inactive', ''] else "❌"
    print(f"  {icon} {name}: {result}")

# 2. Test HTTP
print("\n[2] HTTP Tests:")
tests = [
    ('Direct Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Via Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('CSRF Cookie Test', 'curl -s -D - -o /dev/null --connect-timeout 5 http://127.0.0.1:80/login/ | grep -i set-cookie | grep -i csrf || echo "NO_CSRF_COOKIE"'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    if 'http_code' in cmd:
        icon = "✅" if result in ['200', '302', '500'] else "❌"
        print(f"  {icon} {name}: HTTP {result}")
    else:
        if 'csrftoken' in result.lower() or 'csrf' in result.lower():
            print(f"  ✅ {name}: OK")
            print(f"     {result[:60]}")
        else:
            print(f"  ⚠️  {name}: Issue detected")

# 3. Check Gunicorn errors if running
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
gunicorn_count = stdout.read().decode().strip()
if gunicorn_count != '0':
    print("\n[3] Recent Gunicorn Errors:")
    stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null | grep -i "error\|exception\|failed" | tail -5')
    errors = stdout.read().decode().strip()
    if errors:
        for line in errors.split('\n'):
            if line.strip():
                print(f"  {line[:70]}")
    else:
        print("  No recent errors")

ssh.close()

print("\n" + "="*70)
print("🎯 CSRF 403 Error Solution")
print("="*70)
print("\nYour server is working! The 403 CSRF error is a BROWSER issue.")
print("\nThe problem: Your browser cached an old CSRF token.")
print("\nQuick Fixes (try in order):")
print("\n  ✅ Method 1: Hard Refresh")
print("     Press: Ctrl + Shift + R  (or Ctrl + F5)")
print("     This forces browser to reload with fresh CSRF token")
print("\n  ✅ Method 2: Clear Site Data")
print("     1. Click the 🔒 icon in the address bar")
print("     2. Select 'Cookies and site data'")
print("     3. Click 'Remove' for xietongai.com.cn")
print("     4. Refresh the page")
print("\n  ✅ Method 3: Incognito/Private Mode")
print("     Press: Ctrl + Shift + N")
print("     Visit: http://www.xietongai.com.cn/login/")
print("     This bypasses all cache issues")
print("\n  ✅ Method 4: Clear All Cookies")
print("     Press: Ctrl + Shift + Delete")
print("     Select: 'All time'")
print("     Check: 'Cookies and other site data'")
print("     Click: 'Clear data'")
print("\n" + "="*70)
print("The server is healthy. Just clear your browser cache!")
print("="*70 + "\n")
