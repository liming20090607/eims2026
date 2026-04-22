import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Checking Django Application Errors (HTTP 500)")
print("="*80)

# 1. Check Nginx error log
print("\n[1] Nginx error log (last 20 lines)...")
stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/nginx_error.log 2>/dev/null')
nginx_error = stdout.read().decode().strip()
if nginx_error:
    print(nginx_error)
else:
    print("   No recent nginx errors")

# 2. Check Gunicorn error log
print("\n[2] Gunicorn error log (last 20 lines)...")
stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn.log 2>/dev/null')
gunicorn_error = stdout.read().decode().strip()
if gunicorn_error:
    print(gunicorn_error[-1000:])
else:
    print("   No gunicorn log found, checking stderr...")
    stdin, stdout, stderr = ssh.exec_command('journalctl -u gunicorn --no-pager -n 20 2>/dev/null || tail -20 /var/log/gunicorn/error.log 2>/dev/null')
    alt_log = stdout.read().decode().strip()
    if alt_log:
        print(alt_log[-800:])
    else:
        print("   No error log found")

# 3. Check Django settings for database config
print("\n[3] Checking Django settings...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && python -c "import django; django.setup(); from django.conf import settings; print(f\'DB ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}\'); print(f\'DB NAME: {settings.DATABASES[\"default\"][\"NAME\"]}\'); print(f\'DB HOST: {settings.DATABASES[\"default\"][\"HOST\"]}\')" 2>&1')
db_info = stdout.read().decode().strip()
stderr_output = stderr.read().decode().strip()
if db_info:
    print(db_info)
if stderr_output:
    print(f"   Error: {stderr_output[:500]}")

# 4. Test database connection
print("\n[4] Testing database connection...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && python -c "import pymysql; conn = pymysql.connect(host=\'127.0.0.1\', user=\'eims_user\', password=\'EIMS2026_mysql\', database=\'eimsdb\'); print(\'Database connection: SUCCESS\'); conn.close()" 2>&1')
db_test = stdout.read().decode().strip()
db_error = stderr.read().decode().strip()
if db_test:
    print(f"   {db_test}")
if db_error:
    print(f"   DB Error: {db_error[:300]}")

# 5. Check if there are pending migrations
print("\n[5] Checking for unapplied migrations...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && python manage.py showmigrations 2>&1 | grep -E "(\\[X\\]|\\[ \\])" | head -20')
migrations = stdout.read().decode().strip()
if migrations:
    print("   Migrations status:")
    print(migrations)
else:
    print("   No migration issues found")

# 6. Check urls.py for import errors
print("\n[6] Testing URL configuration...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && python -c "import sys; sys.path.insert(0, \'.\'); import os; os.environ.setdefault(\'DJANGO_SETTINGS_MODULE\', \'eims_app.settings\'); import django; django.setup(); from eims_app.urls import urlpatterns; print(f\'URL patterns loaded: {len(urlpatterns)} routes\')" 2>&1')
url_test = stdout.read().decode().strip()
url_error = stderr.read().decode().strip()
if url_test:
    print(f"   {url_test}")
if url_error:
    print(f"   URL Config Error: {url_error[:500]}")

# 7. Check MySQL service
print("\n[7] MySQL service status...")
stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld && echo "MySQL: RUNNING" || echo "MySQL: NOT RUNNING"')
mysql_status = stdout.read().decode().strip()
print(f"   {mysql_status}")

# 8. Quick test request with full error output
print("\n[8] Making test request with full error details...")
stdin, stdout, stderr = ssh.exec_command('curl -s --connect-timeout 5 http://127.0.0.1:8000/login/ 2>&1 | head -50')
response = stdout.read().decode()
if response:
    # Look for Django error page content
    if 'Django' in response or 'error' in response.lower():
        # Extract error message
        import re
        error_match = re.search(r'<h1[^>]*>(.*?)</h1>', response, re.DOTALL)
        if error_match:
            error_text = error_match.group(1)[:300]
            print(f"   Error found: {error_text}")
        else:
            print(f"   Response preview: {response[:300]}")
    else:
        print(f"   Response: {response[:200]}")
else:
    print("   Empty response")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("HTTP 500 means the server is reachable but Django has an internal error.")
print("Common causes:")
print("  1. Database connection issue")
print("  2. Missing migrations")
print("  3. Import errors in urls.py or views")
print("  4. Settings configuration error")
print("\nPlease share the error details above so I can fix it!")
print("="*80 + "\n")

ssh.close()
