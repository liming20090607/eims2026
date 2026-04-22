import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Fixing urls.py and Running Migrations")
print("="*80)

# Fix urls.py - add missing import
print("\n[1] Checking urls.py for views_index import...")
stdin, stdout, stderr = ssh.exec_command('grep "from.*views_index" /var/www/eims/urls.py | head -5')
imports = stdout.read().decode()
print(f"    Current imports: {imports.strip() if imports.strip() else 'NONE'}")

if 'views_index' not in imports:
    print("\n    [PROBLEM] views_index not imported!")
    print("    Adding import...")
    
    # Add the import after other view imports
    fix_urls = '''sed -i '/^from eims_app/a from . import views_index' /var/www/eims/urls.py'''
    stdin, stdout, stderr = ssh.exec_command(fix_urls)
    exit_code = stdout.channel.recv_exit_status()
    if exit_code == 0:
        print("    [OK] Import added")
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command('grep "views_index" /var/www/eims/urls.py | head -3')
        verify = stdout.read().decode()
        print(f"    Verified: {verify.strip()}")
    else:
        print(f"    [FAIL] Error: {stderr.read().decode()}")
else:
    print("    [OK] views_index already imported")

# Run migrations properly
print("\n[2] Running Django migrations...")
migrate_cmd = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py makemigrations 2>&1 | tail -10'''
stdin, stdout, stderr = ssh.exec_command(migrate_cmd)
time.sleep(10)
makemig_output = stdout.read().decode()
print(makemig_output if makemig_output.strip() else "    No new migrations")

print("\n[3] Applying migrations...")
migrate_apply = '''cd /var/www/eims && source venv/bin/activate && python3 manage.py migrate 2>&1 | tail -30'''
stdin, stdout, stderr = ssh.exec_command(migrate_apply)
time.sleep(20)
migrate_output = stdout.read().decode()
if migrate_output.strip():
    # Show summary
    lines = migrate_output.split('\n')
    for line in lines[-15:]:
        if 'Applying' in line or 'OK' in line or line.strip() == '':
            continue
        print(f"    {line}")
else:
    print("    (No output)")

# Check if tables were created
print("\n[4] Verifying database tables...")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "USE eims; SHOW TABLES;" 2>&1 | grep -v Warning | wc -l')
table_count = stdout.read().decode().strip()
print(f"    Tables created: {table_count}")

if int(table_count) > 0:
    print("    [OK] Database tables exist")
    
    # Check specifically for auth_user
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "USE eims; SELECT COUNT(*) FROM auth_user;" 2>&1 | grep -v Warning')
    user_check = stdout.read().decode().strip()
    print(f"    Users in auth_user: {user_check}")
else:
    print("    [FAIL] No tables created")

# Create superuser
print("\n[5] Creating admin user...")
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
        print("SUCCESS: Created admin user")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin user already exists")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
EOF
'''

stdin, stdout, stderr = ssh.exec_command(create_admin)
time.sleep(5)
admin_result = stdout.read().decode() + stderr.read().decode()
for line in admin_result.split('\n'):
    if line.strip() and 'Warning' not in line and 'Fixed Python' not in line:
        print(f"    {line}")

# Restart Gunicorn
print("\n[6] Restarting Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn')
time.sleep(2)

gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
worker_count = stdout.read().decode().strip()
print(f"    Workers: {worker_count}")

# Final test
print("\n[7] Testing website...")
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_code = stdout.read().decode().strip()
print(f"    HTTP Status: {http_code}")

print("\n" + "="*80)
if http_code in ["200", "302"]:
    print("[SUCCESS] Website is now working!")
    print("="*80)
    print("\nAccess: http://www.xietongai.com.cn/login/")
    print("\nAdmin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
else:
    print(f"[WARNING] HTTP {http_code}")
    print("="*80)
    print("\nChecking error log...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn.log 2>/dev/null | grep -i error | tail -5')
    errors = stdout.read().decode()
    if errors.strip():
        print(errors)
    else:
        print("  No recent errors")

print("\n" + "="*80 + "\n")

ssh.close()
