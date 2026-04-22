#!/usr/bin/env python
"""
Quick Gunicorn diagnostic
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

print("\n🔍 Quick Gunicorn Diagnostic\n")

# 1. Kill all gunicorn
print("[1] Cleaning...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
time.sleep(2)

# 2. Test gunicorn directly
print("[2] Starting Gunicorn manually...")
cmd = 'cd /var/www/eims && /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 1 --timeout 10 eims.wsgi:application 2>&1 &'
ssh.exec_command(cmd)
time.sleep(5)

# 3. Check status
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
print(f"  Workers: {count}")

# 4. Test HTTP
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/')
code = stdout.read().decode().strip()
print(f"  HTTP: {code}")

# 5. Test via Nginx
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/')
nginx_code = stdout.read().decode().strip()
print(f"  Nginx: {nginx_code}")

# 6. Check latest errors
print("\n[3] Latest errors:")
stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn_error.log')
errors = stdout.read().decode().strip()
for line in errors.split('\n')[-10:]:
    if line.strip() and ('error' in line.lower() or 'exception' in line.lower() or 'failed' in line.lower()):
        print(f"  {line[:70]}")

# 7. Test login page content
if code in ['200', '302']:
    print("\n[4] Login page test:")
    stdin, stdout, stderr = ssh.exec_command('curl -s --connect-timeout 3 http://127.0.0.1:80/login/ | grep -o "<title>[^<]*</title>"')
    title = stdout.read().decode().strip()
    print(f"  {title}")

ssh.close()
print("\n✅ Diagnostic complete\n")
