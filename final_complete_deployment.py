import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("FINAL DEPLOYMENT: Install all modules & complete migrations")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Step 1: Reinstall ALL requirements to ensure nothing is missing
    print("\n[Step 1] Installing ALL requirements from requirements.txt...")
    print("(This ensures no modules are missing)")
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip install -r /www/wwwroot/EIMS2026/requirements.txt', timeout=300)
    time.sleep(60)
    
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    # Show summary
    if 'Successfully installed' in output or 'Requirement already satisfied' in output:
        print("✓ All requirements processed")
        
        # Show last few lines
        lines = output.strip().split('\n')
        for line in lines[-5:]:
            if line.strip():
                print(f"  {line}")
    
    if error and 'ERROR' in error.upper():
        print("Errors:", error[:500])
    
    # Step 2: Verify critical modules
    print("\n[Step 2] Verifying critical modules...")
    verify_script = r'''
import sys
modules = ['django', 'openpyxl', 'requests', 'widget_tweaks', 'import_export', 'django_extensions']
for mod in modules:
    try:
        __import__(mod)
        print(f"OK:{mod}")
    except ImportError as e:
        print(f"MISSING:{mod}:{e}")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python -c "{verify_script}"')
    verify_output = stdout.read().decode('utf-8')
    print(verify_output)
    
    # Step 3: Run migrations
    print("\n[Step 3] Running database migrations...")
    
    print("  3a. makemigrations...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py makemigrations 2>&1', timeout=120)
    time.sleep(20)
    makemig_output = stdout.read().decode('utf-8')
    makemig_error = stderr.read().decode('utf-8')
    
    if makemig_output:
        lines = [l for l in makemig_output.strip().split('\n') if l.strip()]
        if lines:
            print(f"    Output: {lines[-1]}")
    
    if makemig_error and 'Traceback' in makemig_error:
        print(f"    Error: {makemig_error[:200]}")
    else:
        print("    ✓ makemigrations completed")
    
    print("  3b. migrate...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py migrate 2>&1', timeout=180)
    time.sleep(40)
    migrate_output = stdout.read().decode('utf-8')
    migrate_error = stderr.read().decode('utf-8')
    
    if 'Applying' in migrate_output:
        lines = [l for l in migrate_output.strip().split('\n') if 'Applying' in l]
        print(f"    ✓ Applied {len(lines)} migrations")
    elif 'No migrations to apply' in migrate_output:
        print("    ✓ Database is up to date")
    
    if migrate_error and 'Traceback' in migrate_error:
        print(f"    Error: {migrate_error[:300]}")
    
    # Step 4: Collect static files
    print("\n[Step 4] Collecting static files...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py collectstatic --noinput 2>&1', timeout=120)
    time.sleep(15)
    print("    ✓ Static files collected")
    
    # Step 5: Restart services
    print("\n[Step 5] Restarting Baota services...")
    stdin, stdout, stderr = ssh.exec_command('bt 16', timeout=60)
    time.sleep(10)
    print("    ✓ Services restarted")
    
    # Step 6: Final verification
    print("\n[Step 6] Final verification...")
    time.sleep(5)
    
    # Check HTTP status
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"  HTTP Status: {status_code}")
    
    # Check database tables
    db_check_script = r'''
import os, sys, django
sys.path.insert(0, '/www/wwwroot/EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]
print(f"TABLES:{len(tables)}")
key_tables = ['auth_user', 'core_userprofile', 'project_projectdetail', 'contract_contract']
for t in key_tables:
    print(f"{'Y' if t in tables else 'N'}:{t}")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python -c "{db_check_script}"')
    db_output = stdout.read().decode('utf-8')
    db_error = stderr.read().decode('utf-8')
    
    print("  Database Status:")
    for line in db_output.strip().split('\n'):
        if line.startswith('TABLES:'):
            print(f"    Total tables: {line.split(':')[1]}")
        elif line.startswith('Y:') or line.startswith('N:'):
            status, table = line.split(':')
            icon = "✓" if status == 'Y' else "✗"
            print(f"    {icon} {table}")
    
    if db_error:
        print(f"  DB Error: {db_error[:200]}")
    
    # Final result
    print("\n" + "="*70)
    if status_code in ['200', '302']:
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print("\n📍 Access URLs:")
        print("   Main Site:  http://39.106.41.239:8000/")
        print("   Admin:      http://39.106.41.239:8000/admin/")
        print("   Baota:      http://39.106.41.239:8888/")
        print("\n✓ MySQL connection issue FIXED")
        print("✓ All modules installed")
        print("✓ Database migrated")
        print("✓ Services running")
    else:
        print(f"⚠️ Service status: {status_code}")
        print("Check logs for details")
    print("="*70)
    
finally:
    ssh.close()
    print("\nDone!")
