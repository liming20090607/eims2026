import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Fixing Django MySQL Connection")
print("="*80)

# Check settings.py database config
print("\n[1] Current database configuration:")
stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES.*=" /var/www/eims/settings.py | head -15')
db_config = stdout.read().decode()
print(db_config)

# The issue is likely that settings.py has wrong password
# Let's check if it's using 'root123' instead of 'EIMS2026_mysql'
if 'root123' in db_config:
    print("\n[PROBLEM FOUND] Settings.py is using wrong password!")
    print("  Current: root123")
    print("  Should be: EIMS2026_mysql")
    
    # Fix the password in settings.py
    print("\n[2] Fixing password in settings.py...")
    fix_cmd = '''sed -i "s/'PASSWORD': 'root123'/'PASSWORD': 'EIMS2026_mysql'/g" /var/www/eims/settings.py'''
    stdin, stdout, stderr = ssh.exec_command(fix_cmd)
    exit_code = stdout.channel.recv_exit_status()
    if exit_code == 0:
        print("    [OK] Password updated")
    else:
        print(f"    [FAIL] Error: {stderr.read().decode()}")
    
    # Verify the change
    print("\n[3] Verifying the fix...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES.*=" /var/www/eims/settings.py | head -15')
    new_config = stdout.read().decode()
    print(new_config)
    
    if 'EIMS2026_mysql' in new_config:
        print("    [OK] Password is now correct")
    else:
        print("    [FAIL] Password not updated")
else:
    print("\n[INFO] Password appears to be correct in settings.py")

# Restart Gunicorn to pick up the new configuration
print("\n[4] Restarting Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn')
time.sleep(2)

gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
worker_count = stdout.read().decode().strip()
print(f"    Gunicorn workers: {worker_count}")

# Test Django connection
print("\n[5] Testing Django database connection...")
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
    print(f"SUCCESS: Connected! Found {count} users")
except Exception as e:
    print(f"ERROR: {e}")
EOF
'''

stdin, stdout, stderr = ssh.exec_command(django_test)
time.sleep(5)
output = stdout.read().decode() + stderr.read().decode()
for line in output.split('\n'):
    if line.strip() and 'Warning' not in line and 'Fixed Python' not in line:
        print(f"    {line}")

# Test HTTP
print("\n[6] Testing HTTP access...")
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_code = stdout.read().decode().strip()
print(f"    HTTP Status: {http_code}")

if http_code == "200":
    print("\n" + "="*80)
    print("[SUCCESS] Website is now working!")
    print("="*80)
    print("\nYou can access: http://www.xietongai.com.cn/login/")
elif http_code == "500":
    print("\n" + "="*80)
    print("[WARNING] Still getting HTTP 500")
    print("="*80)
    print("\nChecking Gunicorn error log...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn.log 2>/dev/null | grep -i error | tail -10')
    errors = stdout.read().decode()
    if errors.strip():
        print(errors)
    else:
        print("  No errors in log")
else:
    print(f"\n[INFO] HTTP Status: {http_code}")

print("\n" + "="*80 + "\n")

ssh.close()
