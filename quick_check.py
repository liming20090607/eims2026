#!/usr/bin/env python
"""
Quick status check after auto-correction deployment
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
print("📊 EIMS2026 SYSTEM STATUS")
print("="*70 + "\n")

# 1. Check settings.py
print("[1] settings.py status:")
stdin, stdout, stderr = ssh.exec_command('wc -l /var/www/eims/eims/settings.py && echo "---" && grep -c "EIMS2026_mysql" /var/www/eims/eims/settings.py')
result = stdout.read().decode().strip()
print(f"  {result}\n")

# 2. Services
print("[2] Services:")
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

# 3. HTTP tests
print("\n[3] HTTP tests:")
tests = [
    ('Local Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Local Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('Server IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
]
for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302', '500'] else "❌"
    print(f"  {icon} {name}: HTTP {code}")

# 4. Auto-correction system
print("\n[4] Auto-correction system:")
stdin, stdout, stderr = ssh.exec_command('test -x /usr/local/bin/eims_auto_fix.sh && echo "Script exists" || echo "Script missing"')
print(f"  Script: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep eims_auto_fix')
cron = stdout.read().decode().strip()
print(f"  Cron: {'✅ Active' if cron else '❌ Not found'}")

stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/auto_correction.log 2>/dev/null')
logs = stdout.read().decode().strip()
if logs:
    print(f"  Last log entry:")
    for line in logs.split('\n')[-3:]:
        print(f"    {line}")

# 5. MySQL connection test
print("\n[5] MySQL connection test:")
test_cmd = """cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
try:
    django.setup()
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    cursor.close()
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(test_cmd)
result = stdout.read().decode().strip()
icon = "✅" if result == 'OK' else "❌"
print(f"  {icon} Django -> MySQL: {result}")

ssh.close()

print("\n" + "="*70)
print("💡 If HTTP tests show 502 or 000:")
print("   - Wait 2 minutes for auto-correction to fix it")
print("   - Or manually check: python check_now.py")
print("\n🎯 Test in browser: http://www.xietongai.com.cn/login/")
print("="*70 + "\n")
