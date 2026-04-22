import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("Testing website after wsgi.py fix...")
print("="*60)

# Test Gunicorn
import time
time.sleep(2)

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
gunicorn_status = stdout.read().decode().strip()
print(f"Gunicorn (8000): HTTP {gunicorn_status}")

# Test Nginx
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
nginx_status = stdout.read().decode().strip()
print(f"Nginx (80): HTTP {nginx_status}")

# Check Gunicorn processes
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
proc_count = stdout.read().decode().strip()
print(f"Gunicorn processes: {proc_count}")

# Check recent Gunicorn error log
print("\nRecent Gunicorn errors:")
stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || tail -5 /var/www/eims/logs/gunicorn.log 2>/dev/null')
error_log = stdout.read().decode().strip()
if error_log:
    for line in error_log.split('\n')[-5:]:
        if line.strip():
            print(f"  {line[:100]}")
else:
    print("  No recent errors")

# Check wsgi.py content
print("\nwsgi.py settings:")
stdin, stdout, stderr = ssh.exec_command('grep DJANGO_SETTINGS_MODULE /var/www/eims/wsgi.py')
wsgi_content = stdout.read().decode().strip()
print(f"  {wsgi_content}")

# Test Django directly
print("\nDjango setup test:")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c "import django; django.setup(); print(\'OK\')" 2>&1')
django_test = stdout.read().decode().strip()
django_err = stderr.read().decode().strip()
if 'OK' in django_test:
    print(f"  {django_test}")
elif django_err:
    print(f"  Error: {django_err[:200]}")

print("\n" + "="*60)
print("Try accessing: http://39.106.41.239/login/")
print("="*60)

ssh.close()
