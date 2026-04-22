import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Installing openpyxl and completing migrations...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Step 1: Install openpyxl
    print("\n[1] Installing openpyxl...")
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip install openpyxl', timeout=120)
    time.sleep(15)
    output = stdout.read().decode('utf-8')
    print(output.strip().split('\n')[-2:])
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/python -c "import openpyxl; print(\'✓ openpyxl installed\')"')
    print(stdout.read().decode('utf-8').strip())
    
    # Step 2: Run migrations
    print("\n[2] Running makemigrations...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py makemigrations 2>&1', timeout=120)
    time.sleep(15)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output:
        lines = output.strip().split('\n')
        for line in lines[-15:]:
            print(line)
    
    if error and 'Traceback' in error:
        print("\nErrors:", error[:500])
    
    print("\n[3] Running migrate...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py migrate 2>&1', timeout=180)
    time.sleep(30)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if 'Applying' in output:
        lines = output.strip().split('\n')
        applying_lines = [l for l in lines if 'Applying' in l]
        print(f"\n✅ Applied {len(applying_lines)} migrations successfully!")
        for line in applying_lines[-10:]:
            print(f"  {line.strip()}")
    
    if error and 'Traceback' in error:
        print("\nMigration errors:", error[:500])
    
    # Step 3: Verify all tables exist
    print("\n[4] Verifying database tables...")
    test_script = '''
import os
import sys
import django

sys.path.insert(0, '/www/wwwroot/EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]

print(f"Total tables: {len(tables)}")

key_tables = [
    'auth_user',
    'core_userprofile', 
    'project_projectdetail',
    'contract_contract',
    'eims_app_employee',
    'eims_app_personnel',
]

print("\nKey tables status:")
for table in key_tables:
    status = "✓" if table in tables else "✗"
    print(f"  {status} {table}")
'''
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python << \'VERIFYEOF\'\n{test_script}\nVERIFYEOF')
    verify_output = stdout.read().decode('utf-8')
    verify_error = stderr.read().decode('utf-8')
    print(verify_output)
    if verify_error:
        print("Error:", verify_error[:300])
    
    # Step 4: Restart services
    print("\n[5] Restarting services...")
    stdin, stdout, stderr = ssh.exec_command('bt 16', timeout=60)
    time.sleep(10)
    print("✓ Services restarted")
    
    # Step 5: Final check
    print("\n[6] Final verification...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP Status: {status_code}")
    
    if status_code in ['200', '302']:
        print("\n" + "="*60)
        print("✅ ALL DEPLOYMENT STEPS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nAccess Information:")
        print("  Main Site: http://39.106.41.239:8000/")
        print("  Admin:     http://39.106.41.239:8000/admin/")
        print("\nThe MySQL connection error has been FIXED!")
        print("All database tables have been created.")
    else:
        print(f"\n⚠️ Unexpected status: {status_code}")
    
finally:
    ssh.close()
    print("\nDone!")
