#!/usr/bin/env python3
"""
Install ALL requirements and start Gunicorn
"""

import paramiko
import os
import time

print("=" * 80)
print("📦 Installing ALL Requirements from requirements.txt")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Install all requirements
print("[1/3] Installing ALL packages from requirements.txt...")
stdin, stdout, stderr = ssh.exec_command(
    f"cd {SERVER_PATH} && source venv/bin/activate && pip install -r requirements.txt",
    timeout=300
)

# Show progress
output_lines = []
while not stdout.channel.exit_status_ready():
    line = stdout.readline()
    if line:
        output_lines.append(line.strip())
        if len(output_lines) > 5:
            output_lines.pop(0)

exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("  ✅ All requirements installed successfully")
else:
    error = stderr.read().decode()
    print(f"  ⚠️ Some packages may have failed")
    print(error[-300:] if len(error) > 300 else error)

# Verify key packages
print("\n[2/3] Verifying critical packages...")
critical_packages = [
    "django",
    "gunicorn",
    "pymysql",
    "django-extensions",
    "django-import-export",
    "openpyxl",
    "pillow"
]

for pkg in critical_packages:
    pkg_import = pkg.replace("-", "_")
    check_cmd = f"cd {SERVER_PATH} && source venv/bin/activate && python -c 'import {pkg_import}; print(\"OK\")' 2>&1"
    stdin, stdout, stderr = ssh.exec_command(check_cmd)
    result = stdout.read().decode().strip()
    if 'OK' in result:
        print(f"  ✅ {pkg}")
    else:
        print(f"  ❌ {pkg} - NOT INSTALLED")

# Start Gunicorn
print("\n[3/3] Starting Gunicorn...")

# Kill old
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)

# Start with proper working directory
start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
export DJANGO_SETTINGS_MODULE=settings && \
nohup gunicorn \
    --chdir {SERVER_PATH} \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
echo "Started PID $!" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
result = stdout.read().decode().strip()
print(f"  {result}")

time.sleep(8)

# Verify
print("\nVerifying Gunicorn...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
count = stdout.read().decode().strip()
print(f"  Processes: {count}")

# Test HTTP
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"  HTTP Status: {http_code}")

if http_code == '200':
    print("\n" + "=" * 80)
    print("✅ SUCCESS! SYSTEM FULLY OPERATIONAL!")
    print("=" * 80)
    print(f"\n🌐 Access URLs:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print(f"\n⏰ Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
else:
    print(f"\n⚠️ HTTP {http_code}")
    print("\nLatest errors:")
    stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log")
    print(stdout.read().decode())

ssh.close()
