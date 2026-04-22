#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug Gunicorn startup failure
"""
import paramiko

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
print("🔍 Debugging Gunicorn Startup Failure")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ Connected\n")
    
    # Get full error logs
    print("[1] Full Gunicorn Error Log (last 50 lines):")
    print("=" * 70)
    _, logs, _ = ssh_exec(ssh, 'tail -50 /var/www/eims/logs/gunicorn_error.log')
    print(logs)
    print("=" * 70)
    
    # Check if wsgi.py exists
    print("\n[2] Check wsgi.py:")
    _, wsgi_check, _ = ssh_exec(ssh, 'ls -lh /var/www/eims/eims/wsgi.py 2>&1')
    print(f"  {wsgi_check}")
    
    # Try to start Gunicorn manually to see error
    print("\n[3] Manual Gunicorn Start Test:")
    _, test_output, test_error = ssh_exec(ssh, '''cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import sys
sys.path.insert(0, '/var/www/eims')
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
try:
    django.setup()
    print('✅ Django setup successful')
except Exception as e:
    print(f'❌ Django setup failed: {e}')
    import traceback
    traceback.print_exc()
"''', timeout=15)
    print(f"  {test_output}")
    if test_error:
        print(f"  Error: {test_error}")
    
    # Check settings.py syntax
    print("\n[4] Settings.py Syntax Check:")
    _, syntax_check, syntax_error = ssh_exec(ssh, '''cd /var/www/eims && /var/www/eims/venv/bin/python -m py_compile eims/settings.py 2>&1''')
    if syntax_error:
        print(f"  ❌ Syntax error: {syntax_error}")
    else:
        print("  ✅ No syntax errors")
    
    # Try Gunicorn test start
    print("\n[5] Gunicorn Test Start:")
    _, gunicorn_test, gunicorn_err = ssh_exec(ssh, '''cd /var/www/eims && timeout 10 /var/www/eims/venv/bin/gunicorn \\
        --bind 127.0.0.1:8000 \\
        --workers 1 \\
        --timeout 10 \\
        --access-logfile - \\
        --error-logfile - \\
        eims.wsgi:application 2>&1 | head -50''', timeout=15)
    print(f"  {gunicorn_test}")
    if gunicorn_err:
        print(f"  Error: {gunicorn_err[:500]}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
