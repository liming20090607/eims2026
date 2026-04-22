#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick status check for MySQL fix
"""
import paramiko
import time

print("=" * 70)
print("Quick MySQL Status Check")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    print("SSH connected")
    
    # Check MySQL
    print("\n[1] MySQL Status:")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysqld | grep -v grep')
    ps_out = stdout.read().decode()
    if ps_out:
        print("MySQL is running")
    else:
        print("MySQL is NOT running!")
    
    # Test MySQL connection
    print("\n[2] Test MySQL CLI:")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" 2>&1')
    time.sleep(2)
    test_out = stdout.read().decode() + stderr.read().decode()
    print(test_out[:200])
    
    # Test PyMySQL
    print("\n[3] Test PyMySQL:")
    test_pymysql = """python3 << 'PYEOF'
import pymysql
try:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='EIMS2026_mysql', database='eims')
    print("SUCCESS")
    conn.close()
except Exception as e:
    print("FAILED: " + str(e))
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(test_pymysql)
    time.sleep(3)
    pymysql_out = stdout.read().decode() + stderr.read().decode()
    print(pymysql_out[:200])
    
    # Check Gunicorn
    print("\n[4] Gunicorn Status:")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    gunicorn_count = stdout.read().decode().strip()
    print("Gunicorn processes: " + gunicorn_count)
    
    # Check error logs
    print("\n[5] Recent Errors:")
    stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    errors = stdout.read().decode()
    if 'Access denied' in errors or 'ERROR' in errors:
        print("ERRORS FOUND:")
        print(errors[-500:])
    else:
        print("No recent errors")
        
finally:
    ssh.close()
