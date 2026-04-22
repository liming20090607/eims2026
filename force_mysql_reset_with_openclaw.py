#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force MySQL Password Reset with OpenClaw Integration
使用OpenClaw强制修复MySQL密码
"""
import paramiko
import time

print("=" * 70)
print("Force MySQL Password Reset with OpenClaw Integration")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    print("SSH connected")
    
    # Step 1: Kill ALL MySQL processes
    print("\n[Step 1] Killing ALL MySQL processes...")
    ssh.exec_command('killall -9 mysqld; killall -9 mysqld_safe; sleep 3')
    time.sleep(5)
    
    # Verify all MySQL processes are dead
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysql | grep -v grep')
    remaining = stdout.read().decode()
    if remaining:
        print("WARNING: Some MySQL processes still running:")
        print(remaining)
        ssh.exec_command('killall -9 -r mysql')
        time.sleep(3)
    else:
        print("All MySQL processes killed")
    
    # Step 2: Remove socket files
    print("\n[Step 2] Cleaning socket files...")
    ssh.exec_command('rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysql.sock.lock')
    time.sleep(1)
    
    # Step 3: Start MySQL with skip-grant-tables
    print("\n[Step 3] Starting MySQL with skip-grant-tables...")
    ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 &')
    time.sleep(8)
    
    # Wait for socket
    print("Waiting for socket...")
    for i in range(10):
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command('test -S /var/lib/mysql/mysql.sock && echo "READY"')
        if 'READY' in stdout.read().decode():
            print(f"Socket ready! ({(i+1)*2}s)")
            break
        print(f"Waiting... ({(i+1)*2}s)")
    
    # Step 4: Reset via socket connection
    print("\n[Step 4] Resetting root password...")
    reset_cmd = """mysql -u root --socket=/var/lib/mysql/mysql.sock << 'ENDSQL'
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
    stdin, stdout, stderr = ssh.exec_command(reset_cmd)
    time.sleep(5)
    result = stdout.read().decode()
    error = stderr.read().decode()
    
    print("Reset result:")
    print(result)
    if error:
        print("Errors:")
        print(error[:500])
    
    # Step 5: Shutdown MySQL
    print("\n[Step 5] Shutting down MySQL...")
    ssh.exec_command('mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown')
    time.sleep(5)
    
    # Step 6: Start MySQL normally
    print("\n[Step 6] Starting MySQL normally...")
    ssh.exec_command('systemctl start mysqld')
    time.sleep(8)
    
    # Step 7: Verify
    print("\n[Step 7] Verifying MySQL...")
    tests = [
        ('mysql -uroot -pEIMS2026_mysql -e "SELECT \'CLI OK\';" 2>&1', 'MySQL CLI'),
        ('cd /var/www/eims/venv/bin && ./python -c "import pymysql; c=pymysql.connect(host=\'127.0.0.1\',user=\'root\',password=\'EIMS2026_mysql\',database=\'eims\'); print(\'PyMySQL OK\'); c.close()" 2>&1', 'PyMySQL'),
    ]
    
    for cmd, name in tests:
        print(f"\n{name}:")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(3)
        out = stdout.read().decode() + stderr.read().decode()
        print(out[:300])
    
    # Step 8: Restart Gunicorn
    print("\n[Step 8] Restarting Gunicorn...")
    ssh.exec_command('pkill -9 -f gunicorn; sleep 2; cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log wsgi:application > /dev/null 2>&1 &')
    time.sleep(8)
    
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

# Test admin
r = client.get('/login/')
if r.status_code == 200:
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode('utf-8'))
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {'username': 'admin', 'password': 'admin123456', 'csrfmiddlewaretoken': csrf}, follow=True)
        print('Admin: ' + ('SUCCESS' if r.status_code in [200, 302] else 'FAILED') + ' (' + str(r.status_code) + ')')

# Test root
r = client.get('/login/')
if r.status_code == 200:
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode('utf-8'))
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {'username': 'root', 'password': 'root123456', 'csrfmiddlewaretoken': csrf}, follow=True)
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
    print("Force reset completed!")
    print("=" * 70)
    
finally:
    ssh.close()
