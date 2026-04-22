#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if comprehensive fix is running and its status
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Check MySQL status
    print("=== MySQL Status ===")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" 2>&1')
    time.sleep(2)
    print(stdout.read().decode() + stderr.read().decode())
    
    # Check Gunicorn
    print("\n=== Gunicorn Status ===")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    print(f"Gunicorn processes: {stdout.read().decode().strip()}")
    
    # Test Django
    print("\n=== Django Test ===")
    test = '''cd /var/www/eims && source venv/bin/activate && python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('✓ Database OK')
except Exception as e:
    print(f'✗ Database Error: {e}')
"'''
    stdin, stdout, stderr = ssh.exec_command(test)
    time.sleep(5)
    print(stdout.read().decode() + stderr.read().decode())
    
finally:
    ssh.close()
