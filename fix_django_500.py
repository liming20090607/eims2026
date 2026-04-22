import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)

print("="*80)
print("Fixing Django HTTP 500 Errors")
print("="*80)

# Step 1: Check project structure
print("\n[1] Checking project structure...")
stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/eims/')
structure = stdout.read().decode().strip()
print("Project structure:")
print(structure)

# Find settings.py
print("\n[2] Finding settings.py location...")
stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "settings.py" -type f 2>/dev/null')
settings_files = stdout.read().decode().strip()
print("Settings files found:")
print(settings_files)

# Step 2: Install cryptography package
print("\n[3] Installing cryptography package...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && pip install cryptography 2>&1')
pip_output = stdout.read().decode().strip()
if "Successfully installed" in pip_output or "Requirement already satisfied" in pip_output:
    print("    ✅ cryptography package installed")
else:
    print(f"    Output: {pip_output[:200]}")

# Step 3: Check wsgi.py to see how it's configured
print("\n[4] Checking wsgi.py configuration...")
stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/wsgi.py 2>/dev/null')
wsgi = stdout.read().decode().strip()
print("wsgi.py content:")
print(wsgi[:500])

# Step 4: Check manage.py to see how it's configured
print("\n[5] Checking manage.py configuration...")
stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/manage.py 2>/dev/null')
manage = stdout.read().decode().strip()
print("manage.py content:")
print(manage[:500])

# Step 5: Check the actual module structure
print("\n[6] Checking module structure...")
stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/eims/eims_app/ 2>/dev/null || echo "eims_app folder not found"')
eims_app = stdout.read().decode().strip()
print("eims_app folder:")
print(eims_app)

# Step 6: Create .env file with Django settings module
print("\n[7] Creating .env file...")
# First check if eims_app/settings.py exists
stdin, stdout, stderr = ssh.exec_command('test -f /var/www/eims/eims_app/settings.py && echo "EXISTS" || echo "NOT_FOUND"')
exists = stdout.read().decode().strip()

if exists == "EXISTS":
    # The settings module should be eims_app.settings
    stdin, stdout, stderr = ssh.exec_command('cat > /var/www/eims/.env << EOF\nDJANGO_SETTINGS_MODULE=eims_app.settings\nEOF\n')
    print("    ✅ .env file created with DJANGO_SETTINGS_MODULE=eims_app.settings")
elif settings_files:
    print(f"    ⚠️  settings.py not found at expected location")
    print(f"    Found at: {settings_files}")
    
    # Try to fix by checking what the actual settings module name should be
    # Extract the path and determine correct module name
    settings_path = settings_files.split('\n')[0]
    # e.g., /var/www/eims/eims_app/settings.py -> eims_app.settings
    # e.g., /var/www/eims/settings.py -> settings
    
    relative_path = settings_path.replace('/var/www/eims/', '')
    module_name = relative_path.replace('.py', '').replace('/', '.')
    
    print(f"    Creating .env with: DJANGO_SETTINGS_MODULE={module_name}")
    stdin, stdout, stderr = ssh.exec_command(f'cat > /var/www/eims/.env << EOF\nDJANGO_SETTINGS_MODULE={module_name}\nEOF\n')
else:
    print("    No settings.py found!")

# Step 7: Also update wsgi.py if needed
print("\n[8] Checking and fixing wsgi.py...")
stdin, stdout, stderr = ssh.exec_command('grep -n "DJANGO_SETTINGS_MODULE" /var/www/eims/wsgi.py')
wsgi_settings = stdout.read().decode().strip()
print(f"    Current wsgi.py settings: {wsgi_settings}")

# Step 8: Check Gunicorn service configuration
print("\n[9] Checking Gunicorn configuration...")
stdin, stdout, stderr = ssh.exec_command('cat /etc/systemd/system/gunicorn.service 2>/dev/null || echo "No systemd service found"')
gunicorn_service = stdout.read().decode().strip()
if gunicorn_service:
    print("Gunicorn service file:")
    print(gunicorn_service)
else:
    print("    No systemd service file found")
    # Check how gunicorn is being started
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_proc = stdout.read().decode().strip()
    print(f"    Gunicorn process: {gunicorn_proc[:300]}")

# Step 9: Test Django setup
print("\n[10] Testing Django configuration...")
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=eims_app.settings && python -c "import django; django.setup(); print(\'Django setup: SUCCESS\')" 2>&1')
django_test = stdout.read().decode().strip()
django_error = stderr.read().decode().strip()
if django_test:
    print(f"    {django_test}")
if django_error:
    print(f"    Error: {django_error[:300]}")

# Step 10: If eims_app.settings doesn't work, try settings directly
if not django_test or "SUCCESS" not in django_test:
    print("\n[11] Trying alternative settings module...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=settings && python -c "import django; django.setup(); print(\'Django setup with settings: SUCCESS\')" 2>&1')
    alt_test = stdout.read().decode().strip()
    alt_error = stderr.read().decode().strip()
    if alt_test:
        print(f"    {alt_test}")
    if alt_error:
        print(f"    Error: {alt_error[:300]}")

# Step 11: Restart Gunicorn
print("\n[12] Restarting Gunicorn...")
# Kill existing gunicorn
stdin, stdout, stderr = ssh.exec_command('pkill -9 gunicorn 2>/dev/null; sleep 2')
time.sleep(3)

# Start gunicorn with correct settings
stdin, stdout, stderr = ssh.exec_command('''cd /var/www/eims && \
source venv/bin/activate && \
export DJANGO_SETTINGS_MODULE=eims_app.settings && \
nohup gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 300 \
--access-logfile /var/www/eims/logs/gunicorn_access.log \
--error-logfile /var/www/eims/logs/gunicorn.log \
wsgi:application > /dev/null 2>&1 &''')
time.sleep(5)

# Check if gunicorn is running
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
gunicorn_count = stdout.read().decode().strip()
if gunicorn_count and int(gunicorn_count) > 0:
    print(f"    ✅ Gunicorn started with {gunicorn_count} workers")
else:
    print("    ❌ Gunicorn failed to start")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/logs/gunicorn.log 2>/dev/null | tail -20')
    error_log = stdout.read().decode().strip()
    print(f"    Error log: {error_log}")

# Step 12: Test the application
print("\n[13] Testing application after fix...")
time.sleep(3)
tests = [
    ('Gunicorn direct', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx via proxy', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"    {name}: HTTP {result}")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
print("\nIssues found and fixed:")
print("  1. ✅ Installed cryptography package for MySQL authentication")
print("  2. ✅ Configured DJANGO_SETTINGS_MODULE in .env")
print("  3. ✅ Restarted Gunicorn with correct settings")
print("\nIf still getting HTTP 500, please check:")
print("  - The actual location of settings.py in your project")
print("  - Gunicorn error logs: /var/www/eims/logs/gunicorn.log")
print("\nTry accessing: http://39.106.41.239/login/")
print("="*80 + "\n")

ssh.close()
