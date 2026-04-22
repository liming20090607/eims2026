#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restart MySQL and verify
重启MySQL并验证
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    print("=" * 60)
    print("Restarting MySQL...")
    print("=" * 60)
    
    # Step 1: Start MySQL
    print("\n[1] Starting MySQL...")
    ssh.exec_command('systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null || mysqld_safe &')
    time.sleep(10)
    
    # Step 2: Check if running
    print("[2] Checking MySQL status...")
    stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld 2>/dev/null || (pgrep mysqld > /dev/null && echo "running" || echo "stopped")')
    status = stdout.read().decode().strip()
    print(f"   Status: {status}")
    
    # Step 3: Test connection
    print("\n[3] Testing MySQL connection...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT \'OK\' as status;" 2>&1')
    result = stdout.read().decode() + stderr.read().decode()
    print(f"   Result: {result.strip()}")
    
    # Step 4: Restart Gunicorn
    print("\n[4] Restarting Gunicorn...")
    ssh.exec_command('pkill -9 -f gunicorn; sleep 2; cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &')
    time.sleep(5)
    
    # Step 5: Final verification
    print("\n[5] Final verification...")
    checks = [
        ('MySQL', 'mysql -uroot -pEIMS2026_mysql -e "SELECT 1;" 2>&1 | grep -i error || echo OK'),
        ('Gunicorn', 'ps aux | grep "[g]unicorn" | wc -l'),
        ('HTTP', 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/'),
    ]
    
    for name, cmd in checks:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode().strip()
        print(f"   {name}: {result}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    
finally:
    ssh.close()
