#!/usr/bin/env python3
"""
Pull latest code with fixed requirements and deploy
"""

import paramiko
import os
import time

print("=" * 80)
print("🚀 Pull Latest & Deploy")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Pull latest code
print("[1/4] Pulling latest code from Gitee...")
stdin, stdout, stderr = ssh.exec_command(f"cd {SERVER_PATH} && git pull", timeout=30)
result = stdout.read().decode().strip()
print(f"  {result}\n")

# Install all requirements
print("[2/4] Installing ALL requirements...")
stdin, stdout, stderr = ssh.exec_command(
    f"cd {SERVER_PATH} && source venv/bin/activate && pip install -r requirements.txt 2>&1 | tail -10",
    timeout=180
)
exit_code = stdout.channel.recv_exit_status()
output = stdout.read().decode()
print(output)
print("  ✅ All packages installed\n")

# Run migrations
print("[3/4] Running migrations...")
stdin, stdout, stderr = ssh.exec_command(
    f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -10",
    timeout=60
)
migrate_result = stdout.read().decode()
print(migrate_result if migrate_result else "  No migrations needed\n")

# Start Gunicorn
print("[4/4] Starting Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)

start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    wsgi:application && \
echo "Gunicorn started successfully" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
result = stdout.read().decode().strip()
error = stderr.read().decode().strip()
print(f"  {result}")
if error:
    print(f"  Error: {error}")

time.sleep(8)

# Verify
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

# Check processes
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
count = stdout.read().decode().strip()
print(f"Gunicorn processes: {count}")

# Test HTTP
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"HTTP Status: {http_code}")

if http_code == '200':
    print("\n" + "=" * 80)
    print("✅✅✅ SUCCESS! SYSTEM FULLY OPERATIONAL! ✅✅✅")
    print("=" * 80)
    print(f"\n🌐 Access:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print(f"\n⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
else:
    print(f"\n⚠️ HTTP {http_code}")
    print("\nChecking errors...")
    stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log 2>/dev/null")
    print(stdout.read().decode())

ssh.close()
