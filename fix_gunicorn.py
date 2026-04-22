#!/usr/bin/env python3
"""
Fix Gunicorn startup issue
"""

import paramiko
import os
import time

print("=" * 80)
print("🔧 Fixing Gunicorn")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Check Gunicorn log
print("[1/3] Checking Gunicorn error log...")
stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log 2>/dev/null || echo 'No error log'")
error_log = stdout.read().decode()
print(error_log)

# Check if gunicorn is installed
print("\n[2/3] Verifying Gunicorn installation...")
stdin, stdout, stderr = ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && which gunicorn && gunicorn --version")
gunicorn_info = stdout.read().decode()
print(gunicorn_info)

# Try to start Gunicorn manually with verbose output
print("\n[3/3] Starting Gunicorn manually...")

# Kill any existing
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null", timeout=5)
time.sleep(2)

# Start with full path and proper environment
start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
python -m gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \
    --daemon \
    wsgi:application && \
echo "Gunicorn started successfully" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
result = stdout.read().decode()
error = stderr.read().decode()
print(f"Result: {result}")
if error:
    print(f"Error: {error}")

time.sleep(5)

# Verify
print("\nVerifying Gunicorn processes...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep")
processes = stdout.read().decode()
print(processes if processes else "No Gunicorn processes found")

# Test HTTP
print("\nTesting HTTP access...")
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"HTTP Status: {http_code}")

if http_code == '200':
    print("\n✅ SUCCESS! Gunicorn is running!")
else:
    print(f"\n⚠️ HTTP returned: {http_code}")
    # Check latest error log
    stdin, stdout, stderr = ssh.exec_command(f"tail -20 {SERVER_PATH}/logs/gunicorn_error.log")
    print("\nLatest errors:")
    print(stdout.read().decode())

ssh.close()
print("\n" + "=" * 80)
