#!/usr/bin/env python3
"""
Install missing packages and test Django directly
"""

import paramiko
import os
import time

print("=" * 80)
print("🔧 Installing Missing Packages & Testing")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Install missing packages
print("[1/4] Installing django-import-export...")
ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && pip install django-import-export -q", timeout=60)
time.sleep(5)
print("  ✅ Done")

print("\n[2/4] Installing Pillow...")
ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && pip install Pillow -q", timeout=60)
time.sleep(5)
print("  ✅ Done")

# Test Django directly
print("\n[3/4] Testing Django setup...")
test_django = f"""cd {SERVER_PATH} && source venv/bin/activate && python manage.py check 2>&1 | head -20"""
stdin, stdout, stderr = ssh.exec_command(test_django, timeout=30)
result = stdout.read().decode()
print(result if result else "No output")

# Try to start Gunicorn with verbose logging
print("\n[4/4] Starting Gunicorn with debug...")
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null", timeout=5)
time.sleep(2)

start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
python -m gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 300 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    wsgi:application 2>&1 | head -50 &
sleep 5 && echo "Started" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
output = stdout.read().decode()
print(output[-500:] if len(output) > 500 else output)

time.sleep(8)

# Check processes
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
count = stdout.read().decode().strip()
print(f"\nGunicorn processes: {count}")

# Test HTTP
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/ 2>&1")
http = stdout.read().decode().strip()
print(f"HTTP Status: {http}")

if http == '200':
    print("\n✅ SUCCESS!")
else:
    print("\n⚠️ Checking latest errors...")
    stdin, stdout, stderr = ssh.exec_command(f"tail -50 {SERVER_PATH}/logs/gunicorn_error.log 2>/dev/null | grep -A5 'Error\\|Exception\\|Traceback' | tail -30")
    errors = stdout.read().decode()
    print(errors if errors else "No specific errors found")

ssh.close()
print("\n" + "=" * 80)
