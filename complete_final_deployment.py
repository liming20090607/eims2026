import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Completing deployment...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Step 1: Install missing Django modules
    print("\n[1] Installing missing Django modules (django-extensions, django-import-export)...")
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip install django-extensions django-import-export', timeout=180)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    # Show last few lines of output
    lines = output.strip().split('\n')
    for line in lines[-10:]:
        print(line)
    
    if error and 'ERROR' in error.upper():
        print("Errors:", error[:500])
    
    # Verify installations
    print("\nVerifying module installations...")
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/python -c "import django_extensions; import import_export; print(\'✓ All modules installed successfully\')"')
    verify_output = stdout.read().decode('utf-8').strip()
    verify_error = stderr.read().decode('utf-8')
    print(verify_output)
    if verify_error:
        print("Verification error:", verify_error[:200])
    
    # Step 2: Run database migrations
    print("\n[2] Running makemigrations...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py makemigrations 2>&1', timeout=120)
    time.sleep(15)
    migration_output = stdout.read().decode('utf-8')
    migration_error = stderr.read().decode('utf-8')
    
    if migration_output:
        print(migration_output[-500:] if len(migration_output) > 500 else migration_output)
    if migration_error and 'Traceback' not in migration_error:
        print(migration_error[-300:] if len(migration_error) > 300 else migration_error)
    
    print("\n[3] Running migrate...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py migrate 2>&1', timeout=180)
    time.sleep(30)
    migrate_output = stdout.read().decode('utf-8')
    migrate_error = stderr.read().decode('utf-8')
    
    # Show summary
    if 'Applying' in migrate_output:
        lines = migrate_output.strip().split('\n')
        print(f"Applied {len([l for l in lines if 'Applying' in l])} migrations")
        # Show last 5 migrations
        applying_lines = [l for l in lines if 'Applying' in l][-5:]
        for line in applying_lines:
            print(f"  {line.strip()}")
    
    if migrate_error and 'Traceback' in migrate_error:
        print("Migration errors:", migrate_error[:500])
    
    # Step 3: Collect static files
    print("\n[4] Collecting static files...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py collectstatic --noinput 2>&1', timeout=120)
    time.sleep(15)
    static_output = stdout.read().decode('utf-8')
    static_error = stderr.read().decode('utf-8')
    
    if 'static files copied' in static_output.lower() or '0 static files copied' in static_output.lower():
        print("✓ Static files collected")
    else:
        print(static_output[-200:] if len(static_output) > 200 else static_output)
    
    # Step 4: Restart Baota services
    print("\n[5] Restarting Baota services...")
    stdin, stdout, stderr = ssh.exec_command('bt 16', timeout=60)
    time.sleep(10)
    restart_output = stdout.read().decode('utf-8')
    print("✓ Services restarted")
    
    # Wait for service to fully start
    print("\nWaiting for service to start...")
    time.sleep(10)
    
    # Step 5: Verify deployment
    print("\n[6] Verifying deployment...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP Status Code: {status_code}")
    
    if status_code in ['200', '302']:
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("\nAccess URLs:")
        print("  - Main site: http://39.106.41.239:8000/")
        print("  - Admin: http://39.106.41.239:8000/admin/")
        print("  - Baota Panel: http://39.106.41.239:8888/")
    else:
        print(f"\n⚠️ Unexpected status code: {status_code}")
        print("Checking error logs...")
        stdin, stdout, stderr = ssh.exec_command('tail -50 /www/wwwroot/EIMS2026/logs/django.log 2>/dev/null || tail -50 /var/log/nginx/error.log 2>/dev/null || echo "No logs found"')
        log_output = stdout.read().decode('utf-8')
        print(log_output[-500:] if len(log_output) > 500 else log_output)
    
    # Step 6: Test database connection from Django
    print("\n[7] Testing Django database connection...")
    test_script = '''import os
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
    print(f"[OK] Database connection successful: {result}")
    
    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"[OK] Found {len(tables)} tables in database")
except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python << \'DBTESTEOF\'\n{test_script}\nDBTESTEOF')
    db_output = stdout.read().decode('utf-8')
    db_error = stderr.read().decode('utf-8')
    print(db_output)
    if db_error:
        print("DB Test Error:", db_error[:300])
    
finally:
    ssh.close()
    print("\n✅ Deployment script completed!")
