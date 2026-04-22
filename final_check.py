import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Final Status Check")
print("="*80)

# Check database tables
print("\n[1] Database tables:")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "USE eims; SHOW TABLES;" 2>&1 | grep -v Warning | wc -l')
table_count = stdout.read().decode().strip()
print(f"    Tables: {table_count}")

if int(table_count) > 0:
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "USE eims; SELECT COUNT(*) as user_count FROM auth_user;" 2>&1 | grep -v Warning')
    users = stdout.read().decode().strip()
    print(f"    Users: {users}")

# Check urls.py
print("\n[2] urls.py imports:")
stdin, stdout, stderr = ssh.exec_command('head -20 /var/www/eims/urls.py | grep -E "^from|^import"')
imports = stdout.read().decode()
print(imports if imports.strip() else "    (No imports found)")

# Test Django directly
print("\n[3] Django test:")
django_test = '''cd /var/www/eims && source venv/bin/activate && python3 -c "
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM auth_user')
count = cursor.fetchone()[0]
print(f'Django DB OK: {count} users')
" 2>&1 | grep -v Warning'''

stdin, stdout, stderr = ssh.exec_command(django_test)
time.sleep(5)
result = stdout.read().decode() + stderr.read().decode()
for line in result.split('\n'):
    if line.strip() and 'Fixed Python' not in line:
        print(f"    {line}")

# Check Gunicorn log for errors
print("\n[4] Recent Gunicorn errors:")
stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/gunicorn.log 2>/dev/null | grep -i "error\|exception\|traceback" | tail -10')
errors = stdout.read().decode()
if errors.strip():
    for line in errors.split('\n')[:10]:
        print(f"    {line[:150]}")
else:
    print("    No errors in log")

# Try accessing the site with verbose output
print("\n[5] HTTP verbose test:")
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ 2>&1 | head -50')
response = stdout.read().decode()
if response.strip():
    # Check if it's an error page
    if 'OperationalError' in response or 'DatabaseError' in response:
        print("    [ERROR] Database error in response")
        # Show the error
        for line in response.split('\n')[:20]:
            if 'Error' in line or 'Exception' in line:
                print(f"    {line[:150]}")
    elif '<!DOCTYPE' in response or '<html' in response:
        print("    [OK] HTML response received")
    else:
        print(f"    Response length: {len(response)} chars")
else:
    print("    No response")

print("\n" + "="*80 + "\n")

ssh.close()
