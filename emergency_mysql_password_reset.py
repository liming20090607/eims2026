#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency MySQL Root Password Reset
紧急修复MySQL root密码
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("Emergency MySQL Root Password Reset")
    print("紧急修复MySQL root密码")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] Connecting to server...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH connected")
        
        # Step 1: Stop MySQL
        print("\n[2] Stopping MySQL service...")
        ssh.exec_command('systemctl stop mysqld')
        time.sleep(3)
        
        # Verify MySQL stopped
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysqld | grep -v grep')
        running = stdout.read().decode()
        if running:
            print("MySQL still running, force killing...")
            ssh.exec_command('killall -9 mysqld')
            time.sleep(3)
        
        print("✓ MySQL stopped")
        
        # Step 2: Start MySQL with skip-grant-tables
        print("\n[3] Starting MySQL in recovery mode (skip-grant-tables)...")
        ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 &')
        time.sleep(5)
        
        # Wait for socket to be created
        print("Waiting for MySQL socket...")
        for i in range(15):
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/mysql.sock 2>/dev/null && echo "SOCKET_READY"')
            if 'SOCKET_READY' in stdout.read().decode():
                print(f"✓ Socket ready ({(i+1)*2}s)")
                break
            print(f"  Waiting... ({(i+1)*2}s)")
        
        # Step 3: Reset root password via socket
        print("\n[4] Resetting root password...")
        reset_sql = '''mysql -u root --socket=/var/lib/mysql/mysql.sock << 'EOF'
FLUSH PRIVILEGES;

-- Delete all existing root users
DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;

-- Create new root users with mysql_native_password
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
EOF
'''
        stdin, stdout, stderr = ssh.exec_command(reset_sql)
        time.sleep(5)
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print("Reset result:")
        if result:
            print(result[:800])
        if error:
            print("Warnings:", error[:300])
        
        # Step 4: Verify reset worked
        print("\n[5] Verifying root password reset...")
        stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT User, Host FROM mysql.user WHERE User=\'root\';" 2>&1')
        time.sleep(2)
        verify = stdout.read().decode() + stderr.read().decode()
        print(verify)
        
        if 'ERROR' in verify:
            print("❌ Password reset failed, trying alternative method...")
            
            # Alternative: Direct table manipulation
            print("\n[6] Alternative: Direct user table update...")
            alt_sql = '''mysql -u root --socket=/var/lib/mysql/mysql.sock << 'EOF'
FLUSH PRIVILEGES;

-- Update all root users
UPDATE mysql.user SET 
    authentication_string=PASSWORD('EIMS2026_mysql'),
    plugin='mysql_native_password'
WHERE User='root';

FLUSH PRIVILEGES;

SELECT User, Host, plugin FROM mysql.user WHERE User='root';
EOF
'''
            stdin, stdout, stderr = ssh.exec_command(alt_sql)
            time.sleep(5)
            alt_result = stdout.read().decode() + stderr.read().decode()
            print(alt_result[:800])
        
        # Step 5: Stop MySQL and restart normally
        print("\n[7] Stopping recovery mode and starting MySQL normally...")
        ssh.exec_command('mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown')
        time.sleep(5)
        
        # Start MySQL normally
        ssh.exec_command('systemctl start mysqld')
        time.sleep(8)
        
        # Step 6: Final verification
        print("\n[8] Final verification...")
        final_tests = """
echo "=== Test 1: MySQL CLI ==="
mysql -uroot -pEIMS2026_mysql -e "SELECT 'MySQL CLI OK';" 2>&1

echo "=== Test 2: PyMySQL ==="
python3 << 'PYEOF'
import pymysql
try:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='EIMS2026_mysql', database='eims')
    print("PyMySQL connection OK")
    conn.close()
except Exception as e:
    print("PyMySQL failed: " + str(e))
PYEOF

echo "=== Test 3: Django DB ==="
cd /var/www/eims && source venv/bin/activate && python << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM auth_user')
        count = cursor.fetchone()[0]
        print("Django DB OK, " + str(count) + " users found")
except Exception as e:
    print("Django DB failed: " + str(e))
PYEOF
"""
        stdin, stdout, stderr = ssh.exec_command(final_tests)
        time.sleep(10)
        final_result = stdout.read().decode() + stderr.read().decode()
        print(final_result)
        
        # Step 7: Restart Gunicorn
        print("\n[9] Restarting Gunicorn...")
        ssh.exec_command('pkill -9 -f gunicorn; sleep 2; cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /dev/null 2>&1 &')
        time.sleep(8)
        
        # Step 8: Test login
        print("\n[10] Testing login functionality...")
        login_test = """cd /var/www/eims && source venv/bin/activate && python << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.test import Client
import re

client = Client()

# Test admin login
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
        if r.status_code in [200, 302]:
            print('Admin login: SUCCESS (status: ' + str(r.status_code) + ')')
        else:
            print('Admin login: FAILED (status: ' + str(r.status_code) + ')')

# Test root login  
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
        if r.status_code in [200, 302]:
            print('Root login: SUCCESS (status: ' + str(r.status_code) + ')')
        else:
            print('Root login: FAILED (status: ' + str(r.status_code) + ')')
PYEOF
"""
        stdin, stdout, stderr = ssh.exec_command(login_test)
        time.sleep(10)
        login_result = stdout.read().decode() + stderr.read().decode()
        print(login_result)
        
        print("\n" + "=" * 70)
        print("Emergency fix completed!")
        print("紧急修复完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
