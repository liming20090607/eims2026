import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Fixing MySQL Database Connection Error")
print("="*80)

# Step 1: Check current settings.py database configuration
print("\n[1] Checking current database configuration...")
stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES" /var/www/eims/settings.py | head -15')
db_config = stdout.read().decode().strip()
print("Current DATABASES config:")
print(db_config)

# Step 2: Check MySQL users
print("\n[2] Checking MySQL users...")
stdin, stdout, stderr = ssh.exec_command("mysql -u root -p'fjkl546#' -e \"SELECT user, host FROM mysql.user;\" 2>&1")
mysql_users = stdout.read().decode().strip()
mysql_err = stderr.read().decode().strip()

if mysql_users:
    print("MySQL users:")
    print(mysql_users)
elif mysql_err:
    print(f"MySQL error: {mysql_err[:200]}")

# Step 3: Try to create/verify eims_user
print("\n[3] Setting up MySQL user 'eims_user'...")

# First try to login with root
mysql_commands = """
mysql -u root -p'fjkl546#' << EOF
-- Create database if not exists
CREATE DATABASE IF NOT EXISTS eimsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if not exists
CREATE USER IF NOT EXISTS 'eims_user'@'localhost' IDENTIFIED BY 'EIMS2026_mysql';

-- Grant privileges
GRANT ALL PRIVILEGES ON eimsdb.* TO 'eims_user'@'localhost';

-- Also create root user with correct password for localhost
ALTER USER 'root'@'localhost' IDENTIFIED BY 'fjkl546#';

-- Flush privileges
FLUSH PRIVILEGES;

-- Show result
SELECT 'Database setup completed successfully' as status;
EOF
"""

stdin, stdout, stderr = ssh.exec_command(mysql_commands)
setup_result = stdout.read().decode().strip()
setup_err = stderr.read().decode().strip()

if setup_result:
    print(setup_result)
if setup_err and 'Warning' not in setup_err:
    print(f"Setup errors: {setup_err[:300]}")

# Step 4: Test database connection with eims_user
print("\n[4] Testing database connection...")
stdin, stdout, stderr = ssh.exec_command("""mysql -u eims_user -p'EIMS2026_mysql' -e "SELECT 'Connection test SUCCESS' as result; USE eimsdb; SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='eimsdb';" 2>&1""")
conn_test = stdout.read().decode().strip()
conn_err = stderr.read().decode().strip()

if conn_test:
    print(f"Connection test: {conn_test}")
if conn_err:
    print(f"Connection error: {conn_err[:300]}")

# Step 5: Update settings.py with correct database credentials
print("\n[5] Updating settings.py database configuration...")

# Create a Python script to update settings.py
update_script = """
import re

settings_file = '/var/www/eims/settings.py'

with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace DATABASES configuration
new_db_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eimsdb',
        'USER': 'eims_user',
        'PASSWORD': 'EIMS2026_mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}'''

# Find and replace DATABASES block
pattern = r"DATABASES\\s*=\\s*\\{[^}]+\\}[^}]*\\}"
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_db_config, content, count=1, flags=re.DOTALL)
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("settings.py updated successfully")
else:
    print("Could not find DATABASES configuration")
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{update_script}"')
update_result = stdout.read().decode().strip()
update_err = stderr.read().decode().strip()

if update_result:
    print(f"Update result: {update_result}")
if update_err:
    print(f"Update error: {update_err[:300]}")

# Step 6: Verify the updated settings
print("\n[6] Verifying updated database configuration...")
stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES" /var/www/eims/settings.py | head -15')
updated_config = stdout.read().decode().strip()
print("Updated DATABASES config:")
print(updated_config)

# Step 7: Test Django database connection
print("\n[7] Testing Django database connection...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c "import django; django.setup(); from django.db import connection; conn = connection.cursor(); print(\'Django DB connection: SUCCESS\')" 2>&1')
django_db_test = stdout.read().decode().strip()
django_db_err = stderr.read().decode().strip()

if "SUCCESS" in django_db_test:
    print(f"    ✅ {django_db_test}")
elif django_db_err:
    print(f"    ❌ {django_db_err[:300]}")

# Step 8: Restart Gunicorn
print("\n[8] Restarting Gunicorn...")
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

# Step 9: Test website
print("\n[9] Testing website after database fix...")
time.sleep(2)

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
gunicorn_status = stdout.read().decode().strip()
print(f"    Gunicorn (8000): HTTP {gunicorn_status}")

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
nginx_status = stdout.read().decode().strip()
print(f"    Nginx (80): HTTP {nginx_status}")

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/')
external_status = stdout.read().decode().strip()
print(f"    External IP (80): HTTP {external_status}")

print("\n" + "="*80)
if external_status in ['200', '302', '301']:
    print("🎉 SUCCESS! Website is fully working now!")
    print("="*80)
    print("\nYou can now access:")
    print("  http://39.106.41.239/login/")
    print("  http://www.xietongai.com.cn/login/")
else:
    print("Still having issues. Checking error logs...")
    print("="*80)
    stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    error_log = stdout.read().decode().strip()
    if error_log:
        print("\nRecent errors:")
        print(error_log[-500:])

print("\n" + "="*80 + "\n")

ssh.close()
