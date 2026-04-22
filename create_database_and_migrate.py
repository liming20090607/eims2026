import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Creating Missing Database")
print("="*80)

# Check existing databases
print("\n[1] Checking existing databases...")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SHOW DATABASES;" 2>&1 | grep -v Warning')
databases = stdout.read().decode()
print(databases)

if 'eims' not in databases.lower():
    print("\n[PROBLEM] Database 'eims' does not exist!")
    
    # Create the database
    print("\n[2] Creating database 'eims'...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"')
    exit_code = stdout.channel.recv_exit_status()
    if exit_code == 0:
        print("    [OK] Database created")
    else:
        error = stderr.read().decode()
        print(f"    [FAIL] Error: {error}")
else:
    print("\n[OK] Database 'eims' exists")

# Check if tables exist
print("\n[3] Checking tables in eims database...")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "USE eims; SHOW TABLES;" 2>&1 | grep -v Warning')
tables = stdout.read().decode()
if tables.strip():
    table_count = len([t for t in tables.split('\n') if t.strip()])
    print(f"    Found {table_count} tables")
    print(tables[:500])  # Show first 500 chars
else:
    print("    [WARNING] No tables found - need to run migrations")
    
    # Run Django migrations
    print("\n[4] Running Django migrations...")
    migrate_cmd = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py migrate --run-syncdb 2>&1 | tail -20'''
    stdin, stdout, stderr = ssh.exec_command(migrate_cmd)
    time.sleep(15)
    migration_output = stdout.read().decode() + stderr.read().decode()
    print(migration_output if migration_output.strip() else "    (No output)")

# Create superuser if needed
print("\n[5] Checking for admin user...")
check_user = '''cd /var/www/eims && source venv/bin/activate && python3 << 'EOF'
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')

try:
    import django
    django.setup()
    
    from django.contrib.auth.models import User
    users = User.objects.filter(is_superuser=True)
    if users.exists():
        for user in users:
            print(f"Found admin: {user.username}")
    else:
        print("NO_ADMIN_USERS")
except Exception as e:
    print(f"ERROR: {e}")
EOF
'''

stdin, stdout, stderr = ssh.exec_command(check_user)
time.sleep(5)
user_check = stdout.read().decode().strip()
print(f"    {user_check}")

if 'NO_ADMIN_USERS' in user_check or not user_check:
    print("\n[6] Creating admin user...")
    create_admin = '''cd /var/www/eims && source venv/bin/activate && python3 << 'EOF'
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')

try:
    import django
    django.setup()
    
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created admin user (password: admin123)")
    else:
        print("Admin user already exists")
except Exception as e:
    print(f"ERROR: {e}")
EOF
'''
    stdin, stdout, stderr = ssh.exec_command(create_admin)
    time.sleep(5)
    result = stdout.read().decode().strip()
    print(f"    {result}")

# Restart Gunicorn
print("\n[7] Restarting Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn')
time.sleep(2)

gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
worker_count = stdout.read().decode().strip()
print(f"    Workers: {worker_count}")

# Final test
print("\n[8] Testing website...")
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_code = stdout.read().decode().strip()
print(f"    HTTP Status: {http_code}")

print("\n" + "="*80)
if http_code in ["200", "302"]:
    print("[SUCCESS] Website is working!")
    print("="*80)
    print("\nAccess: http://www.xietongai.com.cn/login/")
    if 'admin123' in str(locals()):
        print("\nAdmin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
else:
    print(f"[WARNING] HTTP {http_code} - Still having issues")
    print("="*80)

print("\n" + "="*80 + "\n")

ssh.close()
