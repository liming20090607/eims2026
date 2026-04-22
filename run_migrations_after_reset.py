#!/usr/bin/env python3
"""
Run migrations after MySQL reset
"""

import paramiko
import os
import time

print("=" * 80)
print("Run Migrations After MySQL Reset")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

def run(ssh, cmd, desc=""):
    print(f"  {desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    if len(output) > 500:
        output = output[-500:]
    return exit_code, output, error

try:
    # 1. Run migrations
    print("\n[1/3] Running database migrations...")
    run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -20", "Migrate")
    
    # 2. Check MySQL
    print("\n[2/3] Checking MySQL...")
    exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SHOW DATABASES;' 2>&1", "Check DB")
    print(f"  {output}")
    
    # 3. Restart Gunicorn
    print("\n[3/3] Restarting Gunicorn...")
    run(ssh, "pkill -9 -f gunicorn", "Stop")
    time.sleep(3)
    run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", "Start")
    time.sleep(5)
    
    exit_code, output, error = run(ssh, "ps aux | grep '[g]unicorn' | wc -l", "Gunicorn")
    print(f"  Gunicorn: {output} processes")
    
    exit_code, output, error = run(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "HTTP")
    print(f"  HTTP: {output}")
    
    print("\n" + "=" * 80)
    print("MIGRATIONS COMPLETE")
    print("=" * 80)
    print("\nREFRESH YOUR BROWSER:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
