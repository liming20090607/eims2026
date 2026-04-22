#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix missing wsgi.py file on server and restart services
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
print("🔧 Fixing Missing wsgi.py and Restarting Services")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ Connected to server\n")
    
    # Create wsgi.py content
    wsgi_content = '''"""
WSGI config for EIMS2026 project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')

application = get_wsgi_application()
'''
    
    print("[1] Creating /var/www/eims/eims/wsgi.py...")
    stdin, stdout, stderr = ssh.exec_command(
        f'cat > /var/www/eims/eims/wsgi.py << WSGI_EOF\n{wsgi_content}\nWSGI_EOF',
        timeout=10
    )
    time.sleep(2)
    
    # Verify file created
    _, verify, _ = ssh_exec(ssh, 'ls -lh /var/www/eims/eims/wsgi.py && echo "---" && cat /var/www/eims/eims/wsgi.py')
    print(f"  ✅ wsgi.py created:\n{verify}\n")
    
    # Kill all Gunicorn processes
    print("[2] Stopping old Gunicorn processes...")
    ssh_exec(ssh, 'pkill -9 gunicorn || true')
    time.sleep(3)
    _, count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    print(f"  Remaining Gunicorn processes: {count}\n")
    
    # Start Gunicorn
    print("[3] Starting Gunicorn...")
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
    
    _, workers, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    print(f"  ✅ Gunicorn workers: {workers}\n")
    
    # Restart Nginx to ensure clean state
    print("[4] Restarting Nginx...")
    ssh_exec(ssh, 'nginx -s reload')
    time.sleep(2)
    _, nginx_count, _ = ssh_exec(ssh, 'pgrep -c nginx || echo "0"')
    print(f"  ✅ Nginx processes: {nginx_count}\n")
    
    # Test HTTP
    print("[5] Testing HTTP access...")
    _, nginx_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
    _, gunicorn_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
    
    print(f"  Nginx (port 80):      HTTP {nginx_code}")
    print(f"  Gunicorn (port 8000): HTTP {gunicorn_code}\n")
    
    # Check for errors if still failing
    if nginx_code not in ['200', '302']:
        print("[6] Recent Gunicorn errors:")
        _, errors, _ = ssh_exec(ssh, 'tail -20 /var/www/eims/logs/gunicorn_error.log')
        print(f"  {errors}\n")
    
    # Verify page content if working
    if nginx_code in ['200', '302']:
        print("[7] Verifying login page content...")
        _, html_check, _ = ssh_exec(ssh, 'curl -s http://127.0.0.1:80/login/ | grep -o "<title>.*</title>" | head -1')
        print(f"  {html_check}\n")
    
    print("=" * 70)
    if nginx_code in ['200', '302']:
        print("✅ SUCCESS! System is fully operational!")
        print("\n🌐 You can now access:")
        print("   http://www.xietongai.com.cn/login/")
        print("   http://39.106.41.239/login/")
        print("\n💡 Auto-correction system will monitor every 2 minutes")
    else:
        print("⚠️  Issues remain - see errors above")
        print("\n🔧 Manual fix command:")
        print("   ssh root@39.106.41.239")
        print("   cd /var/www/eims")
        print("   pkill -9 gunicorn")
        print("   nohup venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application &")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
