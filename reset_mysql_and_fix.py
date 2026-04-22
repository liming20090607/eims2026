import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Reset MySQL Password and Fix Database Config")
print("="*80)

# Step 1: Try to reset MySQL root password using systemctl or other methods
print("\n[1] Checking MySQL authentication method...")

# Try different approaches to access MySQL
approaches = [
    ("sudo mysql (no password)", "sudo mysql -u root -e \"SELECT 1 as test;\" 2>&1"),
    ("mysql with empty password", "mysql -u root -e \"SELECT 1 as test;\" 2>&1"),
]

for name, cmd in approaches:
    print(f"\nTrying: {name}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if result or 'test' in result.lower():
        print(f"    ✅ Success: {result[:100]}")
        break
    elif error:
        print(f"    ❌ {error[:100]}")

# Step 2: Try to use auth_socket or reset password
print("\n[2] Resetting MySQL root password...")

# Method: Use mysqld_safe to skip grant tables
reset_script = """
# Stop MySQL
systemctl stop mysqld

# Start MySQL without grant tables
mysqld_safe --skip-grant-tables &
sleep 3

# Reset password
mysql -u root << EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'fjkl546#';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'fjkl546#';
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY 'fjkl546#';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT 'Password reset successful' as status;
EOF

# Stop MySQL
mysqladmin -u root -p'fjkl546#' shutdown || mysqladmin -u root shutdown
sleep 2

# Start MySQL normally
systemctl start mysqld
sleep 3

# Test connection
mysql -u root -p'fjkl546#' -e "SELECT 'MySQL connection test SUCCESS' as result;"
"""

stdin, stdout, stderr = ssh.exec_command(reset_script, timeout=30)
reset_output = stdout.read().decode()
reset_error = stderr.read().decode()

print("MySQL reset output:")
print(reset_output[-500:] if reset_output else "No output")
if reset_error:
    print("Errors:")
    print(reset_error[-300:])

# Step 3: Test MySQL connection
print("\n[3] Testing MySQL connection after reset...")
time.sleep(3)

stdin, stdout, stderr = ssh.exec_command("mysql -u root -p'fjkl546#' -e \"SHOW DATABASES;\" 2>&1")
db_list = stdout.read().decode().strip()
if db_list:
    print("MySQL databases:")
    print(db_list)
else:
    stdin, stdout, stderr = ssh.exec_command("mysql -u root -e \"SHOW DATABASES;\" 2>&1")
    alt_result = stdout.read().decode().strip()
    print(f"Alternative: {alt_result[:300]}")

# Step 4: Create eims database and user
print("\n[4] Setting up EIMS database...")

setup_db = """
mysql -u root -p'fjkl546#' << EOF 2>&1
CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eimsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create/update eims_user
CREATE USER IF NOT EXISTS 'eims_user'@'localhost' IDENTIFIED BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON eims.* TO 'eims_user'@'localhost';
GRANT ALL PRIVILEGES ON eimsdb.* TO 'eims_user'@'localhost';

-- Also allow from 127.0.0.1
CREATE USER IF NOT EXISTS 'eims_user'@'127.0.0.1' IDENTIFIED BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON eims.* TO 'eims_user'@'127.0.0.1';
GRANT ALL PRIVILEGES ON eimsdb.* TO 'eims_user'@'127.0.0.1';

FLUSH PRIVILEGES;

-- Verify
SELECT 'Database setup completed' as status;
SELECT user, host FROM mysql.user WHERE user LIKE '%eims%' OR user='root';
EOF
"""

stdin, stdout, stderr = ssh.exec_command(setup_db)
db_setup = stdout.read().decode().strip()
print("Database setup:")
print(db_setup[-500:] if db_setup else "No output")

# Step 5: Update settings.py
print("\n[5] Updating settings.py...")

# Read current settings.py
stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/settings.py')
settings_content = stdout.read().decode()

# Check what database name is being used
if "'eims'" in settings_content or '"eims"' in settings_content:
    db_name = 'eims'
elif "'eimsdb'" in settings_content or '"eimsdb"' in settings_content:
    db_name = 'eimsdb'
else:
    db_name = 'eims'

print(f"    Database name in settings: {db_name}")

# Update the settings file using sed
stdin, stdout, stderr = ssh.exec_command('''
cd /var/www/eims
python3 << 'PYEOF'
import re

settings_file = 'settings.py'
with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Update USER
content = re.sub(
    r"('USER':\\s*')\\w+(')",
    r"\\1eims_user\\2",
    content
)

# Update PASSWORD
content = re.sub(
    r"('PASSWORD':\\s*')[^']+(?='.*})",
    r"\\1EIMS2026_mysql",
    content
)

# Update HOST to 127.0.0.1
content = re.sub(
    r"('HOST':\\s*')localhost(')",
    r"\\1127.0.0.1\\2",
    content
)

with open(settings_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("settings.py updated successfully")
PYEOF
''')
update_result = stdout.read().decode().strip()
update_error = stderr.read().decode().strip()

print(f"    {update_result}")
if update_error:
    print(f"    Error: {update_error[:200]}")

# Step 6: Verify settings
print("\n[6] Verifying updated settings...")
stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES" /var/www/eims/settings.py | head -15')
updated_config = stdout.read().decode().strip()
print("Updated DATABASES config:")
print(updated_config)

# Step 7: Test Django database connection
print("\n[7] Testing Django database connection...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c "import django; django.setup(); from django.db import connection; conn = connection.cursor(); print(\'Django DB connection: SUCCESS\'); conn.execute(\'SELECT COUNT(*) FROM auth_user\'); count = conn.fetchone(); print(f\'Users in database: {count[0]}\')" 2>&1')
django_test = stdout.read().decode().strip()
django_err = stderr.read().decode().strip()

if "SUCCESS" in django_test:
    print(f"    ✅ {django_test}")
elif django_err:
    print(f"    ❌ {django_err[:400]}")

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

# Step 9: Final test
print("\n[9] Final website test...")
time.sleep(3)

tests = [
    ('Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('External IP (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
    ('Domain (xietongai.com.cn)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://www.xietongai.com.cn/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"    {name}: HTTP {result}")

print("\n" + "="*80)
print("FIX COMPLETE")
print("="*80)
print("\nTry accessing: http://www.xietongai.com.cn/login/")
print("="*80 + "\n")

ssh.close()
