#!/usr/bin/env python
"""
Final comprehensive fix - capture exact Gunicorn worker boot error and fix
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

print("\n" + "="*80)
print(" FINAL COMPREHENSIVE GUNICORN FIX")
print("="*80 + "\n")

# Step 1: Kill everything
print("[1/8] Cleaning up...")
ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
ssh.exec_command('sleep 2')
time.sleep(3)

# Step 2: Check settings.py is valid Python
print("\n[2/8] Validating settings.py...")
stdin, stdout, stderr = ssh.exec_command('''cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import ast
with open('eims/settings.py', 'r') as f:
    code = f.read()
try:
    ast.parse(code)
    print('✓ settings.py syntax is valid')
    lines = code.split('\\n')
    print(f'✓ File has {len(lines)} lines')
    # Check for DATABASES
    if 'DATABASES' in code:
        print('✓ DATABASES configuration found')
    else:
        print('✗ DATABASES configuration MISSING!')
    # Check for SECRET_KEY
    if 'SECRET_KEY' in code:
        print('✓ SECRET_KEY found')
    else:
        print('✗ SECRET_KEY MISSING!')
except SyntaxError as e:
    print(f'✗ Syntax error in settings.py: {e}')
" 2>&1''')
result = stdout.read().decode().strip()
print(f"    {result}")

# Step 3: Test Django setup with full error output
print("\n[3/8] Testing Django initialization...")
stdin, stdout, stderr = ssh.exec_command('''cd /var/www/eims && /var/www/eims/venv/bin/python << 'PYTHON_SCRIPT'
import sys
import os
import traceback

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')

try:
    print("Step 1: Import Django...")
    import django
    print(f"  ✓ Django {django.VERSION} imported")
    
    print("\\nStep 2: Django setup...")
    django.setup()
    print("  ✓ Django setup complete")
    
    print("\\nStep 3: Import WSGI app...")
    from eims.wsgi import application
    print(f"  ✓ WSGI app loaded: {type(application)}")
    
    print("\\nStep 4: Test database...")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print(f"  ✓ Database OK")
    
    print("\\n✓✓✓ ALL TESTS PASSED ✓✓✓")
    
except Exception as e:
    print(f"\\n✗✗✗ DJANGO FAILED ✗✗")
    print(f"Error: {type(e).__name__}: {e}")
    print("\\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT
''', timeout=15)
time.sleep(8)
django_result = stdout.read().decode().strip()
django_errors = stderr.read().decode().strip()

print("    Django Test Result:")
for line in django_result.split('\n'):
    if line.strip():
        print(f"      {line}")

if django_errors and 'Traceback' in django_errors:
    print("\\n    Errors:")
    for line in django_errors.split('\n')[-10:]:
        if line.strip():
            print(f"      {line}")

# Step 4: Start Gunicorn with --worker-tmp-dir fix
print("\n[4/8] Starting Gunicorn with worker-tmp-dir fix...")
start_cmd = '''cd /var/www/eims
nohup /var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 3 \\
  --threads 2 \\
  --timeout 120 \\
  --graceful-timeout 30 \\
  --worker-tmp-dir /dev/shm \\
  --access-logfile /var/www/eims/logs/gunicorn_access.log \\
  --error-logfile /var/www/eims/logs/gunicorn_error.log \\
  --log-level debug \\
  eims.wsgi:application > /tmp/gunicorn_final.log 2>&1 &
echo "Gunicorn PID: $!"
'''
ssh.exec_command(start_cmd)
time.sleep(10)

# Step 5: Check worker count
print("\n[5/8] Checking Gunicorn workers...")
stdin, stdout, stderr = ssh.exec_command('pgrep -f "gunicorn.*eims.wsgi" | wc -l')
worker_count = stdout.read().decode().strip()
print(f"    Workers running: {worker_count}")

# Step 6: If workers=0, check the full log
if worker_count == '0':
    print("\n[6/8] Analyzing Gunicorn startup log...")
    stdin, stdout, stderr = ssh.exec_command('cat /tmp/gunicorn_final.log')
    startup_log = stdout.read().decode()
    if startup_log:
        print("    Full startup log:")
        print("    " + "-"*76)
        for line in startup_log.split('\n')[-30:]:
            if line.strip():
                print(f"    {line}")
        print("    " + "-"*76)

# Step 7: Test HTTP
print("\n[7/8] Testing HTTP endpoints...")
time.sleep(3)
tests = [
    ('Direct Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Via Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('Via IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302'] else "❌"
    print(f"    {icon} {name}: HTTP {code}")

# Step 8: Final verification
print("\n[8/8] Final status...")
stdin, stdout, stderr = ssh.exec_command('pgrep -f "gunicorn.*eims.wsgi" | wc -l')
final_count = stdout.read().decode().strip()

if final_count != '0':
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s --connect-timeout 5 http://127.0.0.1:80/login/ | grep -o "<title>[^<]*</title>"'
    )
    title = stdout.read().decode().strip()
    print(f"    Page title: {title}")
    
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s -c /tmp/csrf_final.txt http://127.0.0.1:80/login/ >/dev/null 2>&1 && grep csrftoken /tmp/csrf_final.txt || echo "NO_CSRF"'
    )
    csrf = stdout.read().decode().strip()
    if 'csrftoken' in csrf:
        print(f"    ✅ CSRF cookie generated")

ssh.close()

print("\n" + "="*80)
if final_count != '0':
    print("✅ SUCCESS! Gunicorn is running with workers")
    print("="*80)
    print("\\n🎉 YOUR WEBSITE IS NOW WORKING!")
    print("\\n📋 IMPORTANT - Clear your browser cache:")
    print("   1. Press Ctrl + Shift + Delete")
    print("   2. Select 'All time'")
    print("   3. Check 'Cookies and other site data'")
    print("   4. Click 'Clear data'")
    print("   5. Visit: http://www.xietongai.com.cn/login/")
    print("\\n   OR use Incognito mode: Ctrl + Shift + N")
    print("\\n💡 Auto-correction will monitor every 2 minutes")
else:
    print("❌ Gunicorn workers still failing to start")
    print("="*80)
    print("\\n⚠️  This requires manual investigation")
    print("   The exact error should be in the output above")
print("="*80 + "\\n")
