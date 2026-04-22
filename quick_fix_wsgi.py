import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)

print("="*80)
print("Quick Fix: Update wsgi.py settings module")
print("="*80)

# Step 1: Fix wsgi.py
print("\n[1] Fixing wsgi.py settings module...")
# Replace 'settings_local_mysql' with 'settings'
stdin, stdout, stderr = ssh.exec_command("sed -i \"s/settings_local_mysql/settings/g\" /var/www/eims/wsgi.py")
time.sleep(1)

# Verify the fix
stdin, stdout, stderr = ssh.exec_command("grep 'DJANGO_SETTINGS_MODULE' /var/www/eims/wsgi.py")
result = stdout.read().decode().strip()
print(f"    wsgi.py now: {result}")

# Step 2: Create .env file
print("\n[2] Creating .env file...")
stdin, stdout, stderr = ssh.exec_command('echo "DJANGO_SETTINGS_MODULE=settings" > /var/www/eims/.env')
print("    ✅ .env file created")

# Step 3: Kill old Gunicorn processes
print("\n[3] Stopping old Gunicorn processes...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 gunicorn 2>/dev/null; sleep 2')
time.sleep(3)

# Step 4: Start Gunicorn with correct settings
print("\n[4] Starting Gunicorn with correct settings...")
stdin, stdout, stderr = ssh.exec_command('''cd /var/www/eims && \
source venv/bin/activate && \
export DJANGO_SETTINGS_MODULE=settings && \
nohup gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 300 \
--access-logfile /var/www/eims/logs/gunicorn_access.log \
--error-logfile /var/www/eims/logs/gunicorn_error.log \
wsgi:application >> /var/www/eims/logs/gunicorn_startup.log 2>&1 &''')
time.sleep(5)

# Step 5: Check if Gunicorn is running
print("\n[5] Checking Gunicorn status...")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
if count and int(count) > 0:
    print(f"    ✅ Gunicorn running with {count} processes")
else:
    print("    ❌ Gunicorn not running")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/logs/gunicorn_error.log 2>/dev/null | tail -20')
    error = stdout.read().decode().strip()
    if error:
        print(f"    Error log: {error}")

# Step 6: Test Django setup
print("\n[6] Testing Django setup...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c "import django; django.setup(); print(\'Django setup: SUCCESS\')" 2>&1')
test_result = stdout.read().decode().strip()
test_error = stderr.read().decode().strip()
if "SUCCESS" in test_result:
    print(f"    ✅ {test_result}")
elif test_error:
    print(f"    ❌ {test_error[:200]}")

# Step 7: Test HTTP requests
print("\n[7] Testing HTTP requests...")
time.sleep(3)

tests = [
    ('Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"    {name}: HTTP {result}")

# Step 8: Check recent error logs if still failing
print("\n[8] Checking recent logs...")
stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
gunicorn_log = stdout.read().decode().strip()
if gunicorn_log:
    print("    Gunicorn error log:")
    print(gunicorn_log[-300:])

print("\n" + "="*80)
print("FIX COMPLETE")
print("="*80)
print("\nNow try accessing:")
print("  http://39.106.41.239/login/")
print("  http://www.xietongai.com.cn/login/")
print("="*80 + "\n")

ssh.close()
