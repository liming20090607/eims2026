import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Fixing urls.py - Removing undefined openclaw functions")
print("="*80)

# Step 1: Backup urls.py
print("\n[1] Backing up urls.py...")
stdin, stdout, stderr = ssh.exec_command('cp /var/www/eims/urls.py /var/www/eims/urls.py.backup')
print("    ✅ Backup created: urls.py.backup")

# Step 2: Remove the two problematic lines
print("\n[2] Removing openclaw API endpoints from urls.py...")
# Use sed to delete lines containing openclaw_status and openclaw_trigger_fix
stdin, stdout, stderr = ssh.exec_command('sed -i "/openclaw_status/d" /var/www/eims/urls.py')
stdin, stdout, stderr = ssh.exec_command('sed -i "/openclaw_trigger_fix/d" /var/www/eims/urls.py')
print("    ✅ Removed openclaw API endpoints")

# Step 3: Verify the fix
print("\n[3] Verifying urls.py...")
stdin, stdout, stderr = ssh.exec_command('grep -n "openclaw" /var/www/eims/urls.py')
remaining = stdout.read().decode().strip()
if remaining:
    print(f"    ⚠️  Still found openclaw references:\n{remaining}")
else:
    print("    ✅ No openclaw references remaining")

# Show the first 25 lines to confirm structure
print("\n[4] First 25 lines of urls.py after fix:")
stdin, stdout, stderr = ssh.exec_command('head -25 /var/www/eims/urls.py')
print(stdout.read().decode())

# Step 4: Restart Gunicorn
print("\n[5] Restarting Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pkill -9 gunicorn 2>/dev/null; sleep 2')
time.sleep(3)

# Start fresh Gunicorn
stdin, stdout, stderr = ssh.exec_command('''cd /var/www/eims && \
source venv/bin/activate && \
export DJANGO_SETTINGS_MODULE=settings && \
nohup gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 300 \
--access-logfile /var/www/eims/logs/gunicorn_access.log \
--error-logfile /var/www/eims/logs/gunicorn_error.log \
wsgi:application >> /var/www/eims/logs/gunicorn_startup.log 2>&1 &''')
time.sleep(5)

# Step 5: Check Gunicorn status
print("\n[6] Checking Gunicorn status...")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
if count and int(count) > 0:
    print(f"    ✅ Gunicorn running with {count} processes")
else:
    print("    ❌ Gunicorn not running")

# Step 6: Test Django setup
print("\n[7] Testing Django URL loading...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c "import django; django.setup(); from django.urls import get_resolver; resolver = get_resolver(); print(f\'URL patterns loaded: {len(resolver.url_patterns)} routes\')" 2>&1')
url_test = stdout.read().decode().strip()
url_err = stderr.read().decode().strip()
if "loaded" in url_test:
    print(f"    ✅ {url_test}")
elif url_err:
    print(f"    ❌ Error: {url_err[:300]}")

# Step 7: Test HTTP requests
print("\n[8] Testing HTTP requests...")
time.sleep(2)

tests = [
    ('Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
]

all_success = True
for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"    {name}: HTTP {result}")
    if result not in ['200', '302', '301']:
        all_success = False

# Step 8: If still failing, show error logs
if all_success:
    print("\n" + "="*80)
    print("🎉 SUCCESS! Website should now be working!")
    print("="*80)
    print("\nYou can now access:")
    print("  http://39.106.41.239/login/")
    print("  http://www.xietongai.com.cn/login/")
else:
    print("\n" + "="*80)
    print("Still getting errors. Checking logs...")
    print("="*80)
    stdin, stdout, stderr = ssh.exec_command('tail -15 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    error_log = stdout.read().decode().strip()
    if error_log:
        print("\nRecent errors:")
        print(error_log[-500:])

print("\n" + "="*80 + "\n")

ssh.close()
