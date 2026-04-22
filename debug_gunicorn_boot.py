#!/usr/bin/env python
"""
Debug Gunicorn worker boot failure
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
print("🔍 Gunicorn Worker Boot Failure Debug")
print("="*70 + "\n")

# 1. Kill all existing gunicorn
print("[1] Cleaning up...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
time.sleep(2)

# 2. Test Django setup directly
print("\n[2] Testing Django setup...")
test_django = '''cd /var/www/eims
/var/www/eims/venv/bin/python << 'EOF'
import sys
sys.path.insert(0, '/var/www/eims')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')

try:
    import django
    print("✓ Django imported")
    django.setup()
    print("✓ Django setup complete")
    
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✓ Database connection OK")
    
    from eims.wsgi import application
    print("✓ WSGI application loaded")
    print("\\n✓✓✓ ALL TESTS PASSED ✓✓✓")
except Exception as e:
    print(f"✗✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
EOF
'''

stdin, stdout, stderr = ssh.exec_command(test_django, timeout=15)
time.sleep(5)
result = stdout.read().decode().strip()
errors = stderr.read().decode().strip()

if result:
    print("\nDjango Test Output:")
    print(result)

if errors:
    print("\nDjango Test Errors:")
    print(errors)

# 3. Try starting gunicorn with full debug
print("\n" + "="*70)
print("[3] Starting Gunicorn with DEBUG logging...")
print("="*70 + "\n")

debug_cmd = '''cd /var/www/eims
/var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 1 \\
  --threads 1 \\
  --timeout 30 \\
  --log-level debug \\
  --access-logfile - \\
  --error-logfile - \\
  --preload \\
  eims.wsgi:application 2>&1 | head -100 &
GUNICORN_PID=$!
sleep 8
kill $GUNICORN_PID 2>/dev/null
wait $GUNICORN_PID 2>/dev/null
'''

stdin, stdout, stderr = ssh.exec_command(debug_cmd, timeout=20)
time.sleep(12)
output = stdout.read().decode()
error_output = stderr.read().decode()

print("Gunicorn Debug Output:")
print("-"*70)
if output:
    # Show last 50 lines
    lines = output.split('\n')
    for line in lines[-50:]:
        if line.strip():
            print(line)
print("-"*70)

if error_output:
    print("\nGunicorn Error Output:")
    print("-"*70)
    print(error_output[-1000:])
    print("-"*70)

# 4. Check if any process is running
print("\n[4] Current process status:")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep -E "gunicorn|python" | grep -v grep | head -10')
processes = stdout.read().decode().strip()
if processes:
    print(processes)
else:
    print("  No gunicorn/python processes running")

# 5. Check settings.py
print("\n[5] Settings.py check:")
stdin, stdout, stderr = ssh.exec_command('wc -l /var/www/eims/eims/settings.py && grep -c "DATABASES" /var/www/eims/eims/settings.py')
settings_info = stdout.read().decode().strip()
print(f"  {settings_info}")

# 6. Check if port 8000 is free
print("\n[6] Port 8000 status:")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep :8000 || echo "Port 8000 is FREE"')
port_status = stdout.read().decode().strip()
print(f"  {port_status}")

ssh.close()

print("\n" + "="*70)
print("Debug complete")
print("="*70 + "\n")
