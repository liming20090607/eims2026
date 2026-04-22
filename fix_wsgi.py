#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix missing wsgi.py file on server
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
print("🔧 Fixing Missing wsgi.py File")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ Connected\n")
    
    # Check directory structure
    print("[1] Checking eims directory structure:")
    _, dir_structure, _ = ssh_exec(ssh, 'ls -lah /var/www/eims/eims/')
    print(dir_structure)
    
    # Check if wsgi.py exists anywhere
    print("\n[2] Searching for wsgi.py:")
    _, wsgi_locations, _ = ssh_exec(ssh, 'find /var/www/eims -name wsgi.py -type f 2>/dev/null')
    if wsgi_locations:
        print(f"  Found:\n{wsgi_locations}")
    else:
        print("  ❌ wsgi.py not found anywhere!")
    
    # Check asgi.py and other files
    print("\n[3] Related files:")
    _, asgi_check, _ = ssh_exec(ssh, 'ls -lh /var/www/eims/eims/asgi.py /var/www/eims/eims/__init__.py 2>&1')
    print(f"  {asgi_check}")
    
    # Create wsgi.py if it doesn't exist
    wsgi_content = '''"""
WSGI config for eims project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')

application = get_wsgi_application()
'''
    
    print("\n[4] Creating wsgi.py:")
    stdin, stdout, stderr = ssh.exec_command(
        f'cat > /var/www/eims/eims/wsgi.py << WSGI_EOF\n{wsgi_content}\nWSGI_EOF',
        timeout=10
    )
    time.sleep(2)
    
    # Verify
    _, verify, _ = ssh_exec(ssh, 'ls -lh /var/www/eims/eims/wsgi.py')
    print(f"  {verify}")
    
    # Check content
    _, content_check, _ = ssh_exec(ssh, 'head -10 /var/www/eims/eims/wsgi.py')
    print(f"  Content preview:\n{content_check}")
    
    # Kill existing Gunicorn
    print("\n[5] Restarting Gunicorn:")
    ssh_exec(ssh, 'pkill -9 gunicorn || true')
    import time
    time.sleep(2)
    
    # Start Gunicorn with correct working directory
    start_cmd = '''cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn \\
        --bind 127.0.0.1:8000 \\
        --workers 5 \\
        --timeout 120 \\
        --chdir /var/www/eims \\
        eims.wsgi:application \\
        --access-logfile /var/www/eims/logs/gunicorn_access.log \\
        --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'''
    
    ssh_exec(ssh, start_cmd)
    time.sleep(5)
    
    _, count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    print(f"  Gunicorn workers: {count}")
    
    # Test HTTP
    print("\n[6] HTTP Test:")
    _, nginx_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
    _, gunicorn_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
    
    print(f"  Nginx (80):      HTTP {nginx_code}")
    print(f"  Gunicorn (8000): HTTP {gunicorn_code}")
    
    # Check error logs if still failing
    if nginx_code != '200' and nginx_code != '302':
        print("\n[7] Recent Errors:")
        _, errors, _ = ssh_exec(ssh, 'tail -20 /var/www/eims/logs/gunicorn_error.log')
        print(errors)
    
    print("\n" + "=" * 70)
    if nginx_code in ['200', '302']:
        print("✅ SUCCESS! System is working!")
        print("\n🌐 Access: http://www.xietongai.com.cn/login/")
    else:
        print("⚠️  Still having issues - check errors above")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
