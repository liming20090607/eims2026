#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive MySQL Authentication Fix
彻底修复MySQL认证问题
"""
import paramiko
import time
import json

def main():
    print("=" * 70)
    print("Comprehensive MySQL Authentication Fix")
    print("彻底修复MySQL认证问题")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] Connecting to server...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH connection successful")
        
        # Step 1: Check current MySQL status
        print("\n[2] Checking MySQL status...")
        check_mysql = '''
echo "=== MySQL Process ==="
ps aux | grep mysqld | grep -v grep

echo -e "\\n=== MySQL Port ==="
netstat -tlnp | grep 3306

echo -e "\\n=== Test MySQL CLI ==="
mysql -uroot -pEIMS2026_mysql -e "SELECT User, Host, plugin FROM mysql.user WHERE User='root';" 2>&1

echo -e "\\n=== Check authentication plugin ==="
mysql -uroot -pEIMS2026_mysql -e "SHOW VARIABLES LIKE 'default_authentication_plugin';" 2>&1
'''
        stdin, stdout, stderr = ssh.exec_command(check_mysql)
        time.sleep(3)
        mysql_status = stdout.read().decode() + stderr.read().decode()
        print(mysql_status[:1000])
        
        # Step 2: Stop all Gunicorn processes to prevent connection caching
        print("\n[3] Stopping all Gunicorn processes...")
        stop_gunicorn = '''
pkill -9 -f gunicorn || true
sleep 2
fuser -k 8000/tcp 2>/dev/null || true
sleep 2
echo "Gunicorn stopped"
'''
        ssh.exec_command(stop_gunicorn)
        time.sleep(5)
        
        # Step 3: Check if any process is still using port 8000
        print("\n[4] Verifying port 8000 is free...")
        stdin, stdout, stderr = ssh.exec_command('lsof -i:8000 || echo "Port 8000 is free"')
        port_status = stdout.read().decode()
        print(port_status)
        
        # Step 4: Reset ALL root users in MySQL
        print("\n[5] Resetting ALL root users in MySQL...")
        reset_mysql = '''mysql -uroot -pEIMS2026_mysql << 'ENDSQL'
-- Show current root users
SELECT User, Host, plugin FROM mysql.user WHERE User='root';

-- Drop ALL root users
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'127.0.0.1';
DROP USER IF EXISTS 'root'@'::1';
DROP USER IF EXISTS 'root'@'%';
FLUSH PRIVILEGES;

-- Create fresh root users with mysql_native_password
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- Grant all privileges
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;

-- Verify
SELECT User, Host, plugin FROM mysql.user WHERE User='root';
ENDSQL
'''
        stdin, stdout, stderr = ssh.exec_command(reset_mysql)
        time.sleep(5)
        reset_result = stdout.read().decode() + stderr.read().decode()
        print("MySQL reset result:")
        print(reset_result[:800] if len(reset_result) > 800 else reset_result)
        
        # Step 5: Verify MySQL connections work
        print("\n[6] Verifying MySQL connections...")
        verify_mysql = '''
echo "=== Test localhost ==="
mysql -uroot -pEIMS2026_mysql -h localhost -e "SELECT 'localhost OK';" 2>&1

echo -e "\\n=== Test 127.0.0.1 ==="
mysql -uroot -pEIMS2026_mysql -h 127.0.0.1 -e "SELECT '127.0.0.1 OK';" 2>&1

echo -e "\\n=== Test PyMySQL ==="
python3 << 'PYEOF'
import pymysql
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    print("✓ PyMySQL localhost connection successful")
    conn.close()
except Exception as e:
    print(f"✗ PyMySQL localhost failed: {e}")

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    print("✓ PyMySQL 127.0.0.1 connection successful")
    conn.close()
except Exception as e:
    print(f"✗ PyMySQL 127.0.0.1 failed: {e}")
PYEOF
'''
        stdin, stdout, stderr = ssh.exec_command(verify_mysql)
        time.sleep(5)
        verify_result = stdout.read().decode() + stderr.read().decode()
        print(verify_result)
        
        # Step 6: Clear Django cache and restart Gunicorn
        print("\n[7] Clearing Django cache and restarting Gunicorn...")
        restart_gunicorn = '''
cd /var/www/eims

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clear error logs
> logs/gunicorn_error.log
> logs/gunicorn_access.log

# Start Gunicorn with fresh configuration
source venv/bin/activate
nohup gunicorn --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    --log-level info \
    wsgi:application > /dev/null 2>&1 &

sleep 5
echo "Gunicorn restarted"
ps aux | grep gunicorn | grep -v grep | wc -l
'''
        stdin, stdout, stderr = ssh.exec_command(restart_gunicorn)
        time.sleep(8)
        restart_result = stdout.read().decode()
        print(restart_result)
        
        # Step 7: Test Django login
        print("\n[8] Testing Django login functionality...")
        test_login = '''cd /var/www/eims && source venv/bin/activate && python << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.test import Client
import re

client = Client()

# Test admin login
print("=== Testing admin login ===")
r = client.get('/login/')
if r.status_code == 200:
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode('utf-8'))
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {
            'username': 'admin',
            'password': 'admin123456',
            'csrfmiddlewaretoken': csrf
        }, follow=True)
        print(f"Admin login status: {r.status_code}")
        if r.status_code in [200, 302]:
            print("✓ Admin login SUCCESS")
        else:
            print("✗ Admin login FAILED")
    else:
        print("✗ No CSRF token found")
else:
    print(f"✗ GET /login/ failed: {r.status_code}")

# Test root login
print("\\n=== Testing root login ===")
r = client.get('/login/')
if r.status_code == 200:
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode('utf-8'))
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {
            'username': 'root',
            'password': 'root123456',
            'csrfmiddlewaretoken': csrf
        }, follow=True)
        print(f"Root login status: {r.status_code}")
        if r.status_code in [200, 302]:
            print("✓ Root login SUCCESS")
        else:
            print("✗ Root login FAILED")
PYEOF
'''
        stdin, stdout, stderr = ssh.exec_command(test_login)
        time.sleep(10)
        login_result = stdout.read().decode() + stderr.read().decode()
        print(login_result)
        
        # Step 8: Check for any remaining errors
        print("\n[9] Checking for remaining errors...")
        check_errors = '''
echo "=== Recent Gunicorn errors ==="
tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || echo "No errors"

echo -e "\\n=== Check for Access denied ==="
grep -i "access denied" /var/www/eims/logs/gunicorn_error.log | tail -5 || echo "No Access denied errors"
'''
        stdin, stdout, stderr = ssh.exec_command(check_errors)
        time.sleep(2)
        error_check = stdout.read().decode()
        print(error_check)
        
        print("\n" + "=" * 70)
        print("Fix completed! Please check the results above.")
        print("修复完成！请检查上面的结果。")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
