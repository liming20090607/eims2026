#!/usr/bin/env python
"""
Directly test Gunicorn startup and capture exact error
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
print("🔧 Direct Gunicorn Startup Test")
print("="*70 + "\n")

# Kill any existing processes
print("[1] Cleaning up...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
time.sleep(2)

# Try to start gunicorn in foreground and capture output
print("\n[2] Starting Gunicorn (foreground test)...")
test_cmd = """cd /var/www/eims
timeout 10 /var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 1 \\
  --timeout 30 \\
  --log-level info \\
  --access-logfile - \\
  --error-logfile - \\
  eims.wsgi:application 2>&1
"""

stdin, stdout, stderr = ssh.exec_command(test_cmd, timeout=15)
time.sleep(8)

# Get stdout
output = stdout.read().decode()
error = stderr.read().decode()

print("\n[3] Output captured:")
print("-"*70)
if output:
    print(output[-1000:])  # Last 1000 chars
else:
    print("(No output)")
print("-"*70)

if error:
    print("\n[4] Errors captured:")
    print("-"*70)
    print(error[-1000:])  # Last 1000 chars
    print("-"*70)

# Check if any gunicorn process started
print("\n[5] Checking for running processes...")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
processes = stdout.read().decode().strip()
if processes:
    print("  Running processes:")
    for line in processes.split('\n')[:5]:
        print(f"    {line}")
else:
    print("  No gunicorn processes running")

# Check if port 8000 is listening
print("\n[6] Port 8000 status:")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep :8000')
port_status = stdout.read().decode().strip()
if port_status:
    print(f"  ✅ Port 8000 is listening:")
    print(f"  {port_status}")
else:
    print("  ❌ Port 8000 not listening")

# Try alternative: start with python manage.py runserver
print("\n[7] Testing with Django runserver...")
runserver_cmd = """cd /var/www/eims
timeout 5 /var/www/eims/venv/bin/python manage.py check 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(runserver_cmd)
time.sleep(3)
check_output = stdout.read().decode().strip()
check_error = stderr.read().decode().strip()

if check_output:
    print("  Django check output:")
    for line in check_output.split('\n')[-10:]:
        print(f"    {line}")

if check_error:
    print("  Django check errors:")
    for line in check_error.split('\n')[-10:]:
        print(f"    {line}")

ssh.close()

print("\n" + "="*70)
print("Test complete")
print("="*70 + "\n")
