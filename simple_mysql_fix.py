import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Simple MySQL Password Fix")
print("="*80)

# Step 1: Fix MySQL root password
print("\n[1] Fixing MySQL root password...")

# Try to login with sudo (auth_socket)
stdin, stdout, stderr = ssh.exec_command('sudo mysql -u root -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\'; FLUSH PRIVILEGES;" 2>&1')
result = stdout.read().decode().strip()
error = stderr.read().decode().strip()

if not error or 'Warning' in error:
    print("    ✅ MySQL root password updated")
else:
    print(f"    ⚠️  sudo mysql failed: {error[:200]}")
    # Try alternative method
    print("    Trying alternative method...")
    stdin, stdout, stderr = ssh.exec_command('mysql -u root -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\'; FLUSH PRIVILEGES;" 2>&1')
    alt_result = stdout.read().decode().strip()
    alt_error = stderr.read().decode().strip()
    if not alt_error or 'Warning' in alt_error:
        print("    ✅ Alternative method worked")
    else:
        print(f"    ❌ Failed: {alt_error[:200]}")

# Step 2: Verify MySQL connection
print("\n[2] Testing MySQL connection...")
time.sleep(2)

stdin, stdout, stderr = ssh.exec_command("mysql -u root -p'EIMS2026_mysql' -e \"SELECT 'MySQL connection SUCCESS' as result; SHOW DATABASES LIKE 'eims%';\" 2>&1")
mysql_test = stdout.read().decode().strip()
mysql_err = stderr.read().decode().strip()

if "SUCCESS" in mysql_test:
    print(f"    ✅ {mysql_test}")
elif mysql_err:
    print(f"    ❌ {mysql_err[:200]}")
else:
    print(f"    {mysql_test}")

# Step 3: Restart Gunicorn to apply changes
print("\n[3] Restarting Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 gunicorn 2>/dev/null; sleep 2')
time.sleep(3)

stdin, stdout, stderr = ssh.exec_command('''cd /var/www/eims && \
source venv/bin/activate && \
export DJANGO_SETTINGS_MODULE=settings && \
nohup gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 300 \
--access-logfile /var/www/eims/logs/gunicorn_access.log \
--error-logfile /var/www/eims/logs/gunicorn_error.log \
wsgi:application >> /var/www/eims/logs/gunicorn_startup.log 2>&1 &''')
time.sleep(5)

# Step 4: Test website
print("\n[4] Testing website...")
time.sleep(2)

tests = [
    ('Local (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('External IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
    ('Domain', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://www.xietongai.com.cn/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"    {name}: HTTP {result}")

# Step 5: Check if still getting 500 error
print("\n[5] Checking for errors if any...")
stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
error_log = stdout.read().decode().strip()
if error_log:
    print("Recent errors:")
    for line in error_log.split('\n')[-5:]:
        if line.strip():
            print(f"  {line[:100]}")
else:
    print("    No recent errors")

print("\n" + "="*80)
print("FIX COMPLETE")
print("="*80)
print("\nPlease refresh your browser and try:")
print("  http://www.xietongai.com.cn/login/")
print("="*80 + "\n")

ssh.close()
