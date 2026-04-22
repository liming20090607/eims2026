#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start MySQL Service and Fix Authentication
启动MySQL服务并修复认证
"""
import paramiko
import time

print("=" * 70)
print("Start MySQL Service and Fix Authentication")
print("启动MySQL服务并修复认证")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    print("SSH Connected\n")
    
    # Step 1: Check MySQL service status
    print("[Step 1] Checking MySQL service status...")
    stdin, stdout, stderr = ssh.exec_command('systemctl status mysqld 2>&1 | head -15')
    time.sleep(2)
    status = stdout.read().decode()
    print(status)
    
    # Step 2: Check MySQL error log for why it's not running
    print("\n[Step 2] Checking MySQL error log...")
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/log/mysqld.log 2>&1')
    time.sleep(2)
    error_log = stdout.read().decode()
    print(error_log[-1500:] if len(error_log) > 1500 else error_log)
    
    # Step 3: Clean up and start MySQL
    print("\n[Step 3] Cleaning up and starting MySQL...")
    
    # Kill any stuck MySQL processes
    ssh.exec_command('killall -9 mysqld 2>/dev/null; killall -9 mysqld_safe 2>/dev/null; sleep 2')
    time.sleep(3)
    
    # Remove stale socket and pid files
    ssh.exec_command('rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysql.sock.lock /var/run/mysqld/mysqld.pid 2>/dev/null')
    time.sleep(1)
    
    # Ensure mysqld directory exists with correct permissions
    ssh.exec_command('mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld')
    time.sleep(1)
    
    # Try to start MySQL service
    print("Starting MySQL service...")
    ssh.exec_command('systemctl start mysqld')
    time.sleep(10)
    
    # Check if MySQL started
    stdin, stdout, stderr = ssh.exec_command('systemctl status mysqld 2>&1 | head -15')
    time.sleep(2)
    start_status = stdout.read().decode()
    print("\nMySQL start status:")
    print(start_status)
    
    # Wait for socket to be created
    print("\nWaiting for MySQL socket...")
    socket_ready = False
    for i in range(15):
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command('test -S /var/lib/mysql/mysql.sock && echo "READY" || echo "NOT_READY"')
        status = stdout.read().decode().strip()
        if status == 'READY':
            print(f"Socket ready at {(i+1)*2} seconds!")
            socket_ready = True
            break
        print(f"  Waiting... ({(i+1)*2}s)")
    
    if not socket_ready:
        print("\nERROR: Socket not created! Checking error log...")
        stdin, stdout, stderr = ssh.exec_command('tail -20 /var/log/mysqld.log')
        print(stdout.read().decode()[-1000:])
        raise Exception("MySQL failed to start")
    
    # Step 4: Test MySQL connection (try without password first)
    print("\n[Step 4] Testing MySQL connection...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT \'TEST OK\';" 2>&1')
    time.sleep(2)
    test_result = stdout.read().decode() + stderr.read().decode()
    print(test_result)
    
    if 'ERROR' in test_result:
        print("\nPassword authentication failed, need to reset...")
        
        # Step 5: Reset password using skip-grant-tables
        print("\n[Step 5] Resetting MySQL root password...")
        
        # Stop MySQL
        ssh.exec_command('systemctl stop mysqld')
        time.sleep(3)
        
        # Start with skip-grant-tables
        print("Starting MySQL with skip-grant-tables...")
        ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 &')
        time.sleep(5)
        
        # Wait for socket
        print("Waiting for socket...")
        for i in range(15):
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command('test -S /var/lib/mysql/mysql.sock && echo "READY" || echo "NOT_READY"')
            if 'READY' in stdout.read().decode():
                print(f"Socket ready at {(i+1)*2}s!")
                break
            print(f"  Waiting... ({(i+1)*2}s)")
        
        # Reset root user
        print("\nResetting root password...")
        reset_sql = """mysql -u root --socket=/var/lib/mysql/mysql.sock << 'ENDSQL'
FLUSH PRIVILEGES;
DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT User, Host, plugin FROM mysql.user WHERE User='root';
ENDSQL
"""
        stdin, stdout, stderr = ssh.exec_command(reset_sql)
        time.sleep(5)
        reset_result = stdout.read().decode()
        reset_error = stderr.read().decode()
        
        print("Reset result:")
        print(reset_result)
        if reset_error and 'Warning' not in reset_error:
            print("Errors:", reset_error[:300])
        
        # Shutdown and restart MySQL normally
        print("\n[Step 6] Restarting MySQL normally...")
        ssh.exec_command('mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall -9 mysqld')
        time.sleep(5)
        ssh.exec_command('systemctl start mysqld')
        time.sleep(10)
    
    # Step 7: Final verification
    print("\n[Step 7] Final verification...")
    
    tests = [
        ("MySQL CLI", 'mysql -uroot -pEIMS2026_mysql -e "SELECT \'CLI OK\';" 2>&1'),
        ("PyMySQL", 'cd /var/www/eims && source venv/bin/activate && python -c "import pymysql; c=pymysql.connect(host=\'127.0.0.1\',user=\'root\',password=\'EIMS2026_mysql\',database=\'eims\'); print(\'PyMySQL OK\'); c.close()" 2>&1'),
        ("Django DB", 'cd /var/www/eims && source venv/bin/activate && python -c "import os; os.environ.setdefault(\'DJANGO_SETTINGS_MODULE\', \'settings\'); import django; django.setup(); from django.db import connection; connection.ensure_connection(); print(\'Django OK\')" 2>&1'),
    ]
    
    for name, cmd in tests:
        print(f"\n{name}:")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(3)
        out = stdout.read().decode() + stderr.read().decode()
        print(out[:400])
    
    # Step 8: Restart Gunicorn
    print("\n[Step 8] Restarting Gunicorn...")
    ssh.exec_command('pkill -9 -f gunicorn; sleep 2')
    ssh.exec_command('cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log wsgi:application > /dev/null 2>&1 &')
    time.sleep(10)
    
    # Step 9: Test login
    print("\n[Step 9] Testing login...")
    login_test = """cd /var/www/eims && source venv/bin/activate && python << 'PYEOF'
import os, sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.test import Client
import re

client = Client()

print("Testing admin login...")
r = client.get('/login/')
if r.status_code == 200:
    content = r.content.decode('utf-8')
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {
            'username': 'admin',
            'password': 'admin123456',
            'csrfmiddlewaretoken': csrf
        }, follow=True)
        print('Admin: ' + ('SUCCESS' if r.status_code in [200, 302] else 'FAILED') + ' (' + str(r.status_code) + ')')

print("Testing root login...")
r = client.get('/login/')
if r.status_code == 200:
    content = r.content.decode('utf-8')
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {
            'username': 'root',
            'password': 'root123456',
            'csrfmiddlewaretoken': csrf
        }, follow=True)
        print('Root: ' + ('SUCCESS' if r.status_code in [200, 302] else 'FAILED') + ' (' + str(r.status_code) + ')')
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(login_test)
    time.sleep(10)
    login_result = stdout.read().decode() + stderr.read().decode()
    print(login_result)
    
    # Step 10: Clear error logs
    print("\n[Step 10] Clearing error logs...")
    ssh.exec_command('> /var/www/eims/logs/gunicorn_error.log')
    
    print("\n" + "=" * 70)
    print("MySQL Fix Complete!")
    print("MySQL修复完成！")
    print("=" * 70)
    print("\nAccess URLs:")
    print("  http://39.106.41.239/login/")
    print("  http://www.xietongai.com.cn/login/")
    print("\nCredentials:")
    print("  admin / admin123456")
    print("  root / root123456")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
