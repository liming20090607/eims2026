#!/usr/bin/env python3
"""
Install missing dependencies and start Gunicorn
"""

import paramiko
import os
import time

print("=" * 80)
print("📦 Installing Missing Dependencies")
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
print("[1/2] Installing django-extensions and other dependencies...")
packages = [
    "django-extensions",
    "PyMySQL",
    "openpyxl",
    "pillow",
    "requests",
    "python-dateutil"
]

for package in packages:
    print(f"  Installing {package}...")
    stdin, stdout, stderr = ssh.exec_command(
        f"cd {SERVER_PATH} && source venv/bin/activate && pip install {package} -q",
        timeout=60
    )
    exit_code = stdout.channel.recv_exit_status()
    if exit_code == 0:
        print(f"    ✅ {package} installed")
    else:
        error = stderr.read().decode().strip()
        print(f"    ⚠️ {package} failed: {error[:100]}")

print("\n[2/2] Starting Gunicorn...")

# Kill old processes
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null", timeout=5)
time.sleep(2)

# Start Gunicorn
start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
sleep 3 && echo "Gunicorn started" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
result = stdout.read().decode().strip()
print(f"  {result}")

time.sleep(5)

# Verify
print("\nVerifying...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"  Gunicorn processes: {count}")

# Test HTTP
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}\\n' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"  HTTP Status: {http_code}")

if http_code == '200':
    print("\n" + "=" * 80)
    print("✅ SYSTEM IS FULLY OPERATIONAL!")
    print("=" * 80)
    print(f"\n🌐 Access:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print(f"\n⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
else:
    print(f"\n⚠️ Still having issues (HTTP {http_code})")
    print("\nLatest errors:")
    stdin, stdout, stderr = ssh.exec_command(f"tail -20 {SERVER_PATH}/logs/gunicorn_error.log")
    print(stdout.read().decode())

ssh.close()
