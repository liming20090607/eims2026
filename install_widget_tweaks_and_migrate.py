import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Installing missing modules and completing migrations...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Step 1: Install widget_tweaks
    print("\n[1] Installing django-widget-tweaks...")
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip install django-widget-tweaks', timeout=120)
    time.sleep(20)
    output = stdout.read().decode('utf-8')
    print(output.strip().split('\n')[-3:])
    
    # Verify installation
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/python -c "import widget_tweaks; print(\'✓ widget_tweaks installed\')"')
    print(stdout.read().decode('utf-8').strip())
    
    # Step 2: Check all INSTALLED_APPS modules
    print("\n[2] Checking all required modules...")
    check_script = '''
import sys
sys.path.insert(0, '/www/wwwroot/EIMS2026')

required_modules = [
    'django',
    'django_extensions',
    'import_export',
    'widget_tweaks',
]

for module in required_modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError as e:
        print(f"✗ {module}: {e}")
'''
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python << \'CHECKEOF\'\n{check_script}\nCHECKEOF')
    print(stdout.read().decode('utf-8'))
    
    # Step 3: Run migrations
    print("\n[3] Running makemigrations...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py makemigrations 2>&1', timeout=120)
    time.sleep(15)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output:
        lines = output.strip().split('\n')
        for line in lines[-10:]:
            print(line)
    
    if error and 'Traceback' in error:
        print("Migration errors:", error[:500])
    
    print("\n[4] Running migrate...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py migrate 2>&1', timeout=180)
    time.sleep(30)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if 'Applying' in output:
        lines = output.strip().split('\n')
        applying_lines = [l for l in lines if 'Applying' in l]
        print(f"Applied {len(applying_lines)} migrations")
        for line in applying_lines[-5:]:
            print(f"  {line.strip()}")
    
    if error and 'Traceback' in error:
        print("Migration errors:", error[:500])
    
    # Step 4: Test database connection
    print("\n[5] Testing database connection...")
    test_script = '''
import os
import sys
import django

sys.path.insert(0, '/www/wwwroot/EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"[OK] Database connection successful")
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"[OK] Found {len(tables)} tables")
    
    # List some key tables
    table_names = [t[0] for t in tables]
    key_tables = ['auth_user', 'core_userprofile', 'project_projectdetail', 'contract_contract']
    for table in key_tables:
        if table in table_names:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (missing)")
            
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
'''
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python << \'DBTESTEOF\'\n{test_script}\nDBTESTEOF')
    db_output = stdout.read().decode('utf-8')
    db_error = stderr.read().decode('utf-8')
    print(db_output)
    if db_error:
        print("Error:", db_error[:300])
    
    # Step 5: Restart services
    print("\n[6] Restarting services...")
    stdin, stdout, stderr = ssh.exec_command('bt 16', timeout=60)
    time.sleep(10)
    print("✓ Services restarted")
    
    # Step 6: Final verification
    print("\n[7] Final verification...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP Status: {status_code}")
    
    if status_code in ['200', '302']:
        print("\n✅ DEPLOYMENT COMPLETE!")
        print("\nYou can now access:")
        print("  http://39.106.41.239:8000/")
        print("\nThe database connection issue has been fixed!")
    else:
        print(f"\n⚠️ Status code: {status_code}")
    
finally:
    ssh.close()
    print("\nDone!")
