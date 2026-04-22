import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("DEBUGGING HTTP 500 ERROR")
print("="*80)

# Test Django directly
print("\n[1] Testing Django database connection:")
django_test = '''cd /var/www/eims && source venv/bin/activate && python3 << 'EOF'
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')

try:
    import django
    django.setup()
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"SUCCESS: {count} users found")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
EOF
'''

stdin, stdout, stderr = ssh.exec_command(django_test)
time.sleep(5)
output = stdout.read().decode() + stderr.read().decode()
for line in output.split('\n'):
    if line.strip() and 'Warning' not in line and 'Fixed Python' not in line:
        print(f"  {line}")

# Check Gunicorn error log
print("\n[2] Gunicorn error log (last 20 lines):")
stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn.log 2>/dev/null || echo "No log"')
gunicorn_log = stdout.read().decode()
if gunicorn_log.strip():
    # Show only error lines
    for line in gunicorn_log.split('\n'):
        if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
            print(f"  {line[:200]}")
    if not any(keyword in gunicorn_log.lower() for keyword in ['error', 'exception', 'traceback']):
        print("  No errors in log")
else:
    print("  (Empty log)")

# Check if there's a specific Django error
print("\n[3] Testing HTTP with verbose output:")
stdin, stdout, stderr = ssh.exec_command('curl -v http://127.0.0.1:8000/login/ 2>&1 | grep -E "HTTP/|< " | head -20')
verbose_output = stdout.read().decode()
if verbose_output.strip():
    for line in verbose_output.split('\n')[:15]:
        print(f"  {line}")

# Check settings.py database config
print("\n[4] Database configuration in settings.py:")
stdin, stdout, stderr = ssh.exec_command('grep -A 8 "DATABASES.*=" /var/www/eims/settings.py | head -12')
db_config = stdout.read().decode()
print(db_config if db_config.strip() else "  (Cannot read)")

# Check if there are pending migrations
print("\n[5] Checking for pending migrations:")
migration_check = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py showmigrations 2>&1 | grep -E "\[ \]" | head -5'''
stdin, stdout, stderr = ssh.exec_command(migration_check)
time.sleep(3)
pending = stdout.read().decode()
if pending.strip():
    print("  Pending migrations found:")
    for line in pending.split('\n')[:5]:
        print(f"    {line}")
else:
    print("  No pending migrations")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
print("\nIf you see database errors above, the issue is:")
print("  - Django cannot connect to MySQL even though CLI can")
print("  - This might be a socket vs TCP connection issue")
print("\nTry this fix:")
print("  python e:\\EIMS2026\\fix_django_mysql_connection.py")

print("\n" + "="*80 + "\n")

ssh.close()
