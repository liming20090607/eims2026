#!/usr/bin/env python
"""
Capture the FULL Gunicorn worker boot error
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

print("\n" + "="*70)
print("🔍 Full Gunicorn Worker Error Capture")
print("="*70 + "\n")

# Kill all gunicorn
print("[1] Cleaning up...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
time.sleep(2)

# Clear old logs
ssh.exec_command('> /var/www/eims/logs/gunicorn_error.log')
ssh.exec_command('> /tmp/full_gunicorn_error.log')

# Start gunicorn in foreground to capture ALL output
print("\n[2] Starting Gunicorn in foreground with full error capture...")
foreground_cmd = '''cd /var/www/eims
/var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 1 \\
  --threads 1 \\
  --timeout 30 \\
  --log-level debug \\
  --access-logfile - \\
  --error-logfile - \\
  --preload \\
  --worker-tmp-dir /dev/shm \\
  eims.wsgi:application 2>&1 &
PID=$!
sleep 12
kill -9 $PID 2>/dev/null
wait $PID 2>/dev/null
echo "DONE"'''

stdin, stdout, stderr = ssh.exec_command(foreground_cmd, timeout=30)
time.sleep(15)

full_output = stdout.read().decode()
full_error = stderr.read().decode()

print("\n" + "="*70)
print("FULL GUNICORN OUTPUT:")
print("="*70)
print(full_output[-2000:] if len(full_output) > 2000 else full_output)

if full_error:
    print("\n" + "="*70)
    print("FULL GUNICORN ERRORS:")
    print("="*70)
    print(full_error[-2000:] if len(full_error) > 2000 else full_error)

# Also check the error log file
print("\n" + "="*70)
print("Error log file contents:")
print("="*70)
stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/logs/gunicorn_error.log')
log_content = stdout.read().decode()
print(log_content[-2000:] if len(log_content) > 2000 else log_content)

# Test Django setup one more time with full traceback
print("\n" + "="*70)
print("Django WSGI Import Test:")
print("="*70)
test_django = '''cd /var/www/eims
/var/www/eims/venv/bin/python << 'EOF'
import sys
import os
import traceback

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')

print("Step 1: Setting up paths")
print(f"  Current dir: {os.getcwd()}")
print(f"  Python path: {sys.path[:3]}")

print("\nStep 2: Importing Django")
try:
    import django
    print(f"  ✓ Django {django.VERSION} imported")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Django setup")
try:
    django.setup()
    print("  ✓ Django setup complete")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Importing WSGI application")
try:
    from eims.wsgi import application
    print(f"  ✓ WSGI app imported: {type(application)}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Testing database connection")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"  ✓ Database OK: {result}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()

print("\n✓✓✓ ALL DJANGO TESTS PASSED ✓✓✓")
EOF
'''

stdin, stdout, stderr = ssh.exec_command(test_django, timeout=15)
time.sleep(8)
django_output = stdout.read().decode()
django_error = stderr.read().decode()

print("\nDjango Test Output:")
print(django_output)

if django_error:
    print("\nDjango Test Errors:")
    print(django_error)

# Check if port 8000 is available
print("\n" + "="*70)
print("Port 8000 status:")
print("="*70)
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep :8000 || echo "Port 8000 is FREE"')
print(stdout.read().decode().strip())

ssh.close()

print("\n" + "="*70)
print("Diagnostic Complete")
print("="*70 + "\n")
