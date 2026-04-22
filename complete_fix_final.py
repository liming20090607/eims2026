import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Complete Fix - urls.py and Database")
print("="*80)

# Fix urls.py - use absolute import instead of relative
print("\n[1] Fixing urls.py import...")
fix_import = '''sed -i 's/from \. import views_index/from eims_app import views_index/' /var/www/eims/urls.py'''
stdin, stdout, stderr = ssh.exec_command(fix_import)
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("    [OK] Import fixed")
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command('grep "views_index" /var/www/eims/urls.py | head -1')
    verify = stdout.read().decode().strip()
    print(f"    {verify}")
else:
    print(f"    [FAIL] {stderr.read().decode()}")

# Run migrations with proper error handling
print("\n[2] Running makemigrations...")
makemig = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py makemigrations 2>&1 | tail -15'''
stdin, stdout, stderr = ssh.exec_command(makemig)
time.sleep(10)
makemig_out = stdout.read().decode()
print(makemig_out if makemig_out.strip() else "    No new migrations")

print("\n[3] Running migrate (this may take a minute)...")
migrate = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py migrate --run-syncdb 2>&1 | tail -40'''
stdin, stdout, stderr = ssh.exec_command(migrate)
time.sleep(30)
migrate_out = stdout.read().decode()
if migrate_out.strip():
    lines = migrate_out.split('\n')
    success_count = sum(1 for line in lines if 'OK' in line)
    print(f"    Applied {success_count} migrations")
    # Show any errors
    for line in lines:
        if 'Error' in line or 'Traceback' in line:
            print(f"    ERROR: {line[:150]}")
else:
    print("    (No output)")

# Check tables
print("\n[4] Checking database tables...")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "USE eims; SHOW TABLES;" 2>&1 | grep -v Warning | wc -l')
table_count = stdout.read().decode().strip()
print(f"    Tables: {table_count}")

if int(table_count) > 5:
    print("    [OK] Database has tables")
else:
    print("    [WARN] Not enough tables")
    # Try manual table creation
    print("    Creating tables manually...")
    create_tables = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py migrate --fake-initial 2>&1 | tail -10'''
    stdin, stdout, stderr = ssh.exec_command(create_tables)
    time.sleep(10)
    result = stdout.read().decode()
    print(result if result.strip() else "    (Done)")

# Create admin user
print("\n[5] Creating admin user...")
create_admin = '''cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')

try:
    import django
    django.setup()
    
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("SUCCESS: Admin created")
    else:
        print("Admin exists")
except Exception as e:
    print(f"ERROR: {e}")
PYEOF
'''

stdin, stdout, stderr = ssh.exec_command(create_admin)
time.sleep(5)
admin_result = stdout.read().decode().strip()
print(f"    {admin_result}")

# Restart Gunicorn
print("\n[6] Restarting Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn')
time.sleep(2)

gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
workers = stdout.read().decode().strip()
print(f"    Workers: {workers}")

# Test
print("\n[7] Testing website...")
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_code = stdout.read().decode().strip()
print(f"    HTTP: {http_code}")

print("\n" + "="*80)
if http_code in ["200", "302"]:
    print("[SUCCESS] Website is working!")
    print("="*80)
    print("\nURL: http://www.xietongai.com.cn/login/")
    print("\nAdmin login:")
    print("  Username: admin")
    print("  Password: admin123")
else:
    print(f"[WARNING] HTTP {http_code}")
    print("="*80)
    
    # Show last errors
    print("\nLast errors from Gunicorn log:")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn.log 2>/dev/null | grep -i "error\|exception" | tail -5')
    errors = stdout.read().decode()
    if errors.strip():
        for line in errors.split('\n')[:5]:
            print(f"  {line[:150]}")
    else:
        print("  No errors in log")

print("\n" + "="*80 + "\n")

ssh.close()
