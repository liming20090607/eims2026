#!/usr/bin/env python
"""
Comprehensive Gunicorn crash diagnosis and fix
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
print("🔍 Comprehensive Gunicorn Diagnosis")
print("="*70 + "\n")

# Step 1: Kill all gunicorn processes
print("[1] Cleaning up old processes...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
ssh.exec_command('sleep 2')
time.sleep(3)

# Step 2: Try to import WSGI app directly
print("\n[2] Testing WSGI app import...")
test_import = '''cd /var/www/eims
/var/www/eims/venv/bin/python -c "
import sys
sys.path.insert(0, '/var/www/eims')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eims.settings'
try:
    from eims.wsgi import application
    print('SUCCESS: WSGI app imported')
    print('App type:', type(application))
except Exception as e:
    print('FAILED:', str(e))
    import traceback
    traceback.print_exc()
" 2>&1'''

stdin, stdout, stderr = ssh.exec_command(test_import, timeout=15)
time.sleep(5)
import_result = stdout.read().decode().strip()
import_error = stderr.read().decode().strip()

if import_result:
    print("  Result:")
    for line in import_result.split('\n')[-10:]:
        print(f"    {line}")
if import_error:
    print("  Errors:")
    for line in import_error.split('\n')[-10:]:
        print(f"    {line}")

# Step 3: Try starting gunicorn in foreground with full error output
print("\n[3] Starting Gunicorn in foreground (timeout 10s)...")
start_gunicorn = '''cd /var/www/eims
timeout 10 /var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 1 \\
  --threads 1 \\
  --timeout 30 \\
  --log-level debug \\
  --access-logfile /tmp/gunicorn_access.log \\
  --error-logfile /tmp/gunicorn_error.log \\
  --capture-output \\
  eims.wsgi:application 2>&1 || echo "EXIT_CODE: $?"'''

stdin, stdout, stderr = ssh.exec_command(start_gunicorn, timeout=20)
time.sleep(12)

# Get the output
output = stdout.read().decode()
error = stderr.read().decode()

print("\n  Gunicorn Output:")
print("  " + "-"*68)
if output:
    lines = output.split('\n')
    # Show relevant lines
    for line in lines[-30:]:
        if line.strip():
            print(f"  {line}")
else:
    print("  (No output)")
print("  " + "-"*68)

# Step 4: Check temporary log files
print("\n[4] Checking temporary log files...")
stdin, stdout, stderr = ssh.exec_command('cat /tmp/gunicorn_error.log 2>/dev/null || echo "FILE_NOT_FOUND"')
error_log = stdout.read().decode().strip()
if error_log and error_log != "FILE_NOT_FOUND":
    print("\n  Error Log:")
    for line in error_log.split('\n')[-20:]:
        if line.strip():
            print(f"    {line}")

stdin, stdout, stderr = ssh.exec_command('cat /tmp/gunicorn_access.log 2>/dev/null || echo "FILE_NOT_FOUND"')
access_log = stdout.read().decode().strip()
if access_log and access_log != "FILE_NOT_FOUND":
    print("\n  Access Log:")
    for line in access_log.split('\n')[-10:]:
        if line.strip():
            print(f"    {line}")

# Step 5: Check if gunicorn is running now
print("\n[5] Current Gunicorn status:")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn || echo "0"')
count = stdout.read().decode().strip()
print(f"  Worker processes: {count}")

# Step 6: Try an alternative approach - use Django's runserver temporarily
print("\n[6] Testing with Django runserver...")
test_runserver = '''cd /var/www/eims
timeout 5 /var/www/eims/venv/bin/python manage.py check 2>&1'''

stdin, stdout, stderr = ssh.exec_command(test_runserver)
time.sleep(3)
check_result = stdout.read().decode().strip()
check_error = stderr.read().decode().strip()

if check_result:
    print("  Django check result:")
    for line in check_result.split('\n')[-10:]:
        print(f"    {line}")
if check_error:
    print("  Django check errors:")
    for line in check_error.split('\n')[-10:]:
        print(f"    {line}")

# Step 7: Try starting gunicorn with --reload flag
print("\n[7] Attempting Gunicorn restart with --reload...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
time.sleep(2)

restart_cmd = '''cd /var/www/eims
nohup /var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 3 \\
  --timeout 120 \\
  --reload \\
  --access-logfile /var/www/eims/logs/gunicorn_access.log \\
  --error-logfile /var/www/eims/logs/gunicorn_error.log \\
  --log-level info \\
  eims.wsgi:application > /tmp/gunicorn_start.log 2>&1 &
sleep 5
echo "PID: $(pgrep -c gunicorn)"'''

stdin, stdout, stderr = ssh.exec_command(restart_cmd, timeout=15)
time.sleep(7)
restart_output = stdout.read().decode().strip()
print(f"  {restart_output}")

# Step 8: Final HTTP test
print("\n[8] Final HTTP test:")
time.sleep(3)
tests = [
    ('Direct (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Via Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302'] else "❌"
    print(f"  {icon} {name}: HTTP {code}")

# Step 9: Show latest error log if still failing
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
final_count = stdout.read().decode().strip()
if final_count == '0':
    print("\n[9] Latest Gunicorn errors:")
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    errors = stdout.read().decode().strip()
    if errors:
        for line in errors.split('\n')[-20:]:
            if line.strip() and any(word in line.lower() for word in ['error', 'exception', 'traceback', 'failed']):
                print(f"    {line[:80]}")

ssh.close()

print("\n" + "="*70)
print("Diagnosis Complete")
print("="*70 + "\n")
