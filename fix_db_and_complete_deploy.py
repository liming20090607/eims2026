import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Fixing database configuration...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Step 1: Create .env file with correct database credentials
    print("\n[1] Creating .env file...")
    env_content = """# Database Configuration
DB_NAME=eims
DB_USER=root
DB_PASSWORD=EIMS2026_mysql
DB_HOST=localhost
DB_PORT=3306

# System Configuration
DEBUG=False
ALLOWED_HOSTS=*
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /www/wwwroot/EIMS2026/.env << \'EOF\'\n{env_content}\nEOF')
    time.sleep(2)
    
    # Verify .env file created
    stdin, stdout, stderr = ssh.exec_command('cat /www/wwwroot/EIMS2026/.env')
    print(stdout.read().decode('utf-8'))
    
    # Step 2: Fix settings.py - update DATABASES configuration
    print("\n[2] Updating settings.py database configuration...")
    
    # Read current settings.py
    stdin, stdout, stderr = ssh.exec_command('cat /www/wwwroot/EIMS2026/settings.py')
    current_settings = stdout.read().decode('utf-8')
    
    # Replace the DATABASES section
    old_db_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_dingce',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'dingce': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_dingce',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {"""
    
    new_db_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims',
        'USER': 'root',
        'PASSWORD': 'EIMS2026_mysql',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'dingce': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims',
        'USER': 'root',
        'PASSWORD': 'EIMS2026_mysql',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {"""
    
    if old_db_config in current_settings:
        updated_settings = current_settings.replace(old_db_config, new_db_config)
        
        # Write updated settings.py
        stdin, stdout, stderr = ssh.exec_command(f'cat > /www/wwwroot/EIMS2026/settings.py << \'SETTINGSEOF\'\n{updated_settings}\nSETTINGSEOF')
        time.sleep(3)
        print("[OK] settings.py updated successfully")
    else:
        print("[WARNING] Could not find exact DATABASES pattern in settings.py")
        print("Using Python script to update...")
        
        # Use Python to update settings.py
        python_script = """
import re

with open('/www/wwwroot/EIMS2026/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace database name
content = content.replace("'NAME': 'eims_dingce'", "'NAME': 'eims'")
# Replace password
content = content.replace("'PASSWORD': 'root123'", "'PASSWORD': 'EIMS2026_mysql'")

with open('/www/wwwroot/EIMS2026/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Settings updated successfully")
"""
        stdin, stdout, stderr = ssh.exec_command(f'python3.9 -c "{python_script}"')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        print(output)
        if error:
            print("Error:", error)
    
    # Step 3: Install missing modules
    print("\n[3] Installing missing Django modules...")
    ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip install django-extensions django-import-export', timeout=120)
    time.sleep(30)
    
    # Verify installations
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/python -c "import django_extensions; import import_export; print(\'All modules installed\')"')
    print(stdout.read().decode('utf-8').strip())
    
    # Step 4: Run database migrations
    print("\n[4] Running database migrations...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py makemigrations 2>&1', timeout=120)
    time.sleep(15)
    migration_output = stdout.read().decode('utf-8')
    print(migration_output[:500] if len(migration_output) > 500 else migration_output)
    
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py migrate 2>&1', timeout=120)
    time.sleep(20)
    migrate_output = stdout.read().decode('utf-8')
    print(migrate_output[:500] if len(migrate_output) > 500 else migrate_output)
    
    # Step 5: Collect static files
    print("\n[5] Collecting static files...")
    stdin, stdout, stderr = ssh.exec_command('cd /www/wwwroot/EIMS2026 && /www/wwwroot/EIMS2026/venv/bin/python manage.py collectstatic --noinput 2>&1', timeout=120)
    time.sleep(15)
    static_output = stdout.read().decode('utf-8')
    print("Static files collected")
    
    # Step 6: Restart services
    print("\n[6] Restarting Baota services...")
    stdin, stdout, stderr = ssh.exec_command('bt 16', timeout=60)
    time.sleep(10)
    print("Services restarted")
    
    # Step 7: Verify deployment
    print("\n[7] Verifying deployment...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP Status Code: {status_code}")
    
    if status_code == '302' or status_code == '200':
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("You can now access: http://39.106.41.239:8000/")
    else:
        print(f"\n⚠️ Service returned status: {status_code}")
        print("Check logs for details")
    
    # Test MySQL connection from Django
    print("\n[8] Testing Django database connection...")
    test_script = """
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
    print(f"[OK] Database connection successful: {result}")
except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
"""
    stdin, stdout, stderr = ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/python -c "{test_script}"')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("Error:", error[:500])
    
finally:
    ssh.close()
    print("\nDone!")
