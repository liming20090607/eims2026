#!/usr/bin/env python
"""
Emergency fix: Restart Gunicorn with detailed error capture
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
print(" Emergency Gunicorn Fix")
print("="*70 + "\n")

# Step 1: Kill all gunicorn
print("[1] Killing all Gunicorn processes...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
time.sleep(3)

# Step 2: Clear error logs
print("[2] Clearing error logs...")
ssh.exec_command('> /var/www/eims/logs/gunicorn_error.log')
ssh.exec_command('> /var/www/eims/logs/gunicorn_access.log')
time.sleep(1)

# Step 3: Start Gunicorn in background with error capture
print("[3] Starting Gunicorn...")
start_cmd = '''cd /var/www/eims
nohup /var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 3 \\
  --timeout 120 \\
  --graceful-timeout 30 \\
  --access-logfile /var/www/eims/logs/gunicorn_access.log \\
  --error-logfile /var/www/eims/logs/gunicorn_error.log \\
  --log-level info \\
  --preload \\
  eims.wsgi:application > /tmp/gunicorn_nohup.log 2>&1 &
'''
ssh.exec_command(start_cmd)
time.sleep(8)

# Step 4: Check if it started
print("[4] Checking Gunicorn status...")
stdin, stdout, stderr = ssh.exec_command('pgrep gunicorn | wc -l')
count = stdout.read().decode().strip()
print(f"    Gunicorn workers: {count}")

# Step 5: If still 0, check errors
if count == '0':
    print("\n[5] Checking error details...")
    stdin, stdout, stderr = ssh.exec_command('cat /tmp/gunicorn_nohup.log')
    nohup_log = stdout.read().decode()
    if nohup_log:
        print("    Nohup log:")
        for line in nohup_log.split('\n')[-20:]:
            if line.strip():
                print(f"      {line}")
    
    print("\n    Recent error log:")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn_error.log')
    errors = stdout.read().decode()
    if errors:
        for line in errors.split('\n')[-15:]:
            if line.strip():
                print(f"      {line}")

# Step 6: Test HTTP
print("\n[6] HTTP test...")
time.sleep(3)
tests = [
    ('Gunicorn 8000', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx 80', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302'] else "❌"
    print(f"    {icon} {name}: HTTP {code}")

# Step 7: If working, test login page
if count != '0':
    print("\n[7] Login page test...")
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s --connect-timeout 5 http://127.0.0.1:80/login/ | grep -o "<title>[^<]*</title>"'
    )
    title = stdout.read().decode().strip()
    print(f"    {title}")
    
    # Test CSRF
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s -c /tmp/csrf_emergency.txt http://127.0.0.1:80/login/ >/dev/null && grep csrftoken /tmp/csrf_emergency.txt || echo "NO_CSRF"'
    )
    csrf = stdout.read().decode().strip()
    if 'csrftoken' in csrf:
        print(f"    ✅ CSRF cookie: {csrf[:50]}...")
    else:
        print(f"    ⚠️ CSRF cookie issue")

ssh.close()

print("\n" + "="*70)
if count != '0':
    print("✅ Gunicorn is running!")
    print("\n🎉 NOW IN YOUR BROWSER:")
    print("  1. Press Ctrl+Shift+Delete")
    print("  2. Clear all cookies for xietongai.com.cn")
    print("  3. Visit: http://www.xietongai.com.cn/login/")
    print("  4. OR use Incognito mode: Ctrl+Shift+N")
else:
    print("❌ Gunicorn still failing to start")
    print("\nNeed to investigate Django/Python configuration")
print("="*70 + "\n")
