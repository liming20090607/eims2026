#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Server Diagnostics - MySQL + Services
"""
import paramiko
import time

print("=" * 70)
print("COMPLETE SERVER DIAGNOSTICS")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    print("SSH Connected\n")
    
    # 1. MySQL Process Check
    print("[1] MySQL Processes:")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep -E "mysqld|mysql" | grep -v grep')
    mysql_ps = stdout.read().decode()
    print(mysql_ps if mysql_ps else "No MySQL processes running")
    
    # 2. MySQL Socket Check
    print("\n[2] MySQL Socket:")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/mysql.sock 2>&1')
    print(stdout.read().decode() + stderr.read().decode())
    
    # 3. MySQL CLI Test
    print("\n[3] MySQL CLI Connection:")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT User, Host, plugin FROM mysql.user WHERE User=\'root\';" 2>&1')
    time.sleep(2)
    cli_result = stdout.read().decode() + stderr.read().decode()
    print(cli_result)
    
    # 4. Check MySQL Authentication Plugin
    print("\n[4] MySQL Authentication Plugin:")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SHOW VARIABLES LIKE \'default_authentication_plugin\';" 2>&1')
    time.sleep(2)
    plugin_result = stdout.read().decode() + stderr.read().decode()
    print(plugin_result)
    
    # 5. PyMySQL Test
    print("\n[5] PyMySQL Connection Test:")
    pymysql_test = """cd /var/www/eims && source venv/bin/activate && python -c "
import pymysql
try:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='EIMS2026_mysql', database='eims', port=3306)
    print('SUCCESS - Connected to MySQL')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM auth_user')
    count = cursor.fetchone()[0]
    print('Users in database: ' + str(count))
    conn.close()
except Exception as e:
    print('FAILED - ' + str(e))
" 2>&1
"""
    stdin, stdout, stderr = ssh.exec_command(pymysql_test)
    time.sleep(5)
    print(stdout.read().decode() + stderr.read().decode())
    
    # 6. Gunicorn Status
    print("\n[6] Gunicorn Status:")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_ps = stdout.read().decode()
    print(gunicorn_ps if gunicorn_ps else "No Gunicorn processes")
    
    # 7. Port Check
    print("\n[7] Port Status:")
    stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep -E "8000|80|3306"')
    print(stdout.read().decode())
    
    # 8. Error Log Check
    print("\n[8] Recent Gunicorn Errors:")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn_error.log 2>&1')
    errors = stdout.read().decode()
    print(errors)
    
    # 9. Django Database Test
    print("\n[9] Django Database Test:")
    django_test = """cd /var/www/eims && source venv/bin/activate && python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('Django DB: SUCCESS')
except Exception as e:
    print('Django DB: FAILED - ' + str(e))
" 2>&1
"""
    stdin, stdout, stderr = ssh.exec_command(django_test)
    time.sleep(5)
    print(stdout.read().decode() + stderr.read().decode())
    
    # 10. HTTP Test
    print("\n[10] HTTP Access Test:")
    import urllib.request
    try:
        req = urllib.request.Request('http://39.106.41.239/login/', method='GET')
        req.add_header('Host', 'www.xietongai.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        print('Login page status: ' + str(response.status))
    except Exception as e:
        print('HTTP test failed: ' + str(e))
    
    print("\n" + "=" * 70)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 70)
    
finally:
    ssh.close()
