#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick verification after wsgi.py fix
"""
import paramiko
import time

SSH_HOST = '39.106.41.239'
SSH_USER = 'root'
SSH_PASS = 'EIMS2026_root'

def ssh_exec(ssh, command, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_status, output, error

print("=" * 70)
print("🔍 Verifying System Status After wsgi.py Fix")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ Connected\n")
    
    # Check services
    print("[1] Service Status:")
    _, mysql_status, _ = ssh_exec(ssh, 'systemctl is-active mysqld')
    _, gunicorn_count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    _, nginx_count, _ = ssh_exec(ssh, 'pgrep -c nginx || echo "0"')
    
    print(f"  MySQL:    {mysql_status}")
    print(f"  Gunicorn: {gunicorn_count} workers")
    print(f"  Nginx:    {nginx_count} processes\n")
    
    # If Gunicorn is not running, start it
    if int(gunicorn_count) == 0:
        print("[2] Starting Gunicorn...")
        
        # Kill any stale processes
        ssh_exec(ssh, 'pkill -9 gunicorn || true')
        time.sleep(2)
        
        # Start with correct working directory
        start_cmd = '''cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn \
            --bind 127.0.0.1:8000 \
            --workers 5 \
            --timeout 120 \
            --chdir /var/www/eims \
            eims.wsgi:application \
            --access-logfile /var/www/eims/logs/gunicorn_access.log \
            --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'''
        
        ssh_exec(ssh, start_cmd)
        time.sleep(5)
        
        _, new_count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
        print(f"  ✅ Gunicorn workers: {new_count}\n")
    else:
        print("[2] Gunicorn already running\n")
    
    # Test HTTP
    print("[3] HTTP Tests:")
    _, nginx_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
    _, gunicorn_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
    
    print(f"  Nginx (80):      HTTP {nginx_code}")
    print(f"  Gunicorn (8000): HTTP {gunicorn_code}\n")
    
    # Check errors if needed
    if nginx_code not in ['200', '302']:
        print("[4] Recent Errors:")
        _, errors, _ = ssh_exec(ssh, 'tail -15 /var/www/eims/logs/gunicorn_error.log')
        print(f"  {errors}\n")
    
    # Verify page content
    if nginx_code in ['200', '302']:
        print("[4] Page Content Verification:")
        _, title, _ = ssh_exec(ssh, 'curl -s http://127.0.0.1:80/login/ | grep -o "<title>.*</title>"')
        print(f"  {title}\n")
    
    print("=" * 70)
    if nginx_code in ['200', '302']:
        print("✅ SUCCESS! Login page is accessible!")
        print("\n🌐 Access URLs:")
        print("   http://www.xietongai.com.cn/login/")
        print("   http://39.106.41.239/login/")
    else:
        print("⚠️  System not fully operational yet")
        print("\n📋 Next steps:")
        print("   1. Check error logs above")
        print("   2. Verify wsgi.py exists: ls -lh /var/www/eims/eims/wsgi.py")
        print("   3. Manual restart: cd /var/www/eims && pkill -9 gunicorn && nohup venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application &")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
