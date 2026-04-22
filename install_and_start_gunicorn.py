#!/usr/bin/env python3
"""
Install Gunicorn and start it
"""

import paramiko
import os
import time

print("=" * 80)
print("📦 Installing and Starting Gunicorn")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Step 1: Install gunicorn
print("[1/4] Installing Gunicorn...")
stdin, stdout, stderr = ssh.exec_command(
    f"cd {SERVER_PATH} && source venv/bin/activate && pip install gunicorn",
    timeout=120
)
install_output = stdout.read().decode()
print(install_output[-200:] if len(install_output) > 200 else install_output)

# Verify installation
stdin, stdout, stderr = ssh.exec_command(
    f"cd {SERVER_PATH} && source venv/bin/activate && gunicorn --version"
)
version = stdout.read().decode().strip()
print(f"\n✅ Gunicorn installed: {version}\n")

# Step 2: Kill any existing processes
print("[2/4] Cleaning up old processes...")
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null", timeout=5)
time.sleep(2)
print("  ✅ Done\n")

# Step 3: Start Gunicorn
print("[3/4] Starting Gunicorn...")

start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
echo "Started with PID $!" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=10)
result = stdout.read().decode().strip()
print(f"  {result}\n")

time.sleep(5)

# Step 4: Verify
print("[4/4] Verifying Gunicorn...")

# Check processes
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"  Gunicorn processes: {count}")

# Check if listening on port
stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp | grep 8000")
port_info = stdout.read().decode().strip()
if port_info:
    print(f"  Port 8000: Listening ✅")
else:
    print(f"  Port 8000: Not listening ⚠️")

# Test HTTP
time.sleep(3)
print("\nTesting HTTP access...")
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"  HTTP Status: {http_code}")

if http_code == '200':
    print("\n" + "=" * 80)
    print("✅ SUCCESS! System is fully operational!")
    print("=" * 80)
    print(f"\n🌐 Access URLs:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print(f"\n⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
else:
    print(f"\n⚠️ HTTP returned: {http_code}")
    print("\nChecking error log...")
    stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log 2>/dev/null")
    print(stdout.read().decode())

ssh.close()
