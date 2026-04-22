#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick check after MySQL password fix
"""
import paramiko
import time

SSH_HOST = '39.106.41.239'
SSH_USER = 'root'
SSH_PASS = 'EIMS2026_root'

def ssh_exec(ssh, command, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_status, output, error

print("=" * 70)
print("🔍 Checking System Status After Fix")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ Connected to server\n")
    
    # Check services
    print("[1] Service Status:")
    _, mysql_status, _ = ssh_exec(ssh, 'systemctl is-active mysqld')
    _, gunicorn_count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    _, nginx_count, _ = ssh_exec(ssh, 'pgrep -c nginx || echo "0"')
    
    print(f"  MySQL:    {mysql_status}")
    print(f"  Gunicorn: {gunicorn_count} workers")
    print(f"  Nginx:    {nginx_count} processes\n")
    
    # Check settings.py password
    print("[2] Settings.py Password:")
    _, pwd_lines, _ = ssh_exec(ssh, 'grep "PASSWORD.*EIMS" /var/www/eims/eims/settings.py')
    pwd_count = pwd_lines.count("EIMS2026_mysql")
    print(f"  Found {pwd_count} correct password entries")
    print(f"  Sample: {pwd_lines.split(chr(10))[0] if pwd_lines else 'NOT FOUND'}\n")
    
    # Test MySQL connection
    print("[3] MySQL Connection Test:")
    _, mysql_test, mysql_err = ssh_exec(ssh, 'mysql -u root -p"EIMS2026_mysql" -e "SELECT 1 AS test;" 2>&1')
    if '1' in mysql_test:
        print("  ✅ MySQL connection successful\n")
    else:
        print(f"  ❌ MySQL connection failed: {mysql_err}\n")
    
    # Test HTTP
    print("[4] HTTP Test:")
    _, nginx_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
    _, gunicorn_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
    
    print(f"  Nginx (80):      HTTP {nginx_code}")
    print(f"  Gunicorn (8000): HTTP {gunicorn_code}\n")
    
    # Check Gunicorn error logs
    print("[5] Recent Gunicorn Errors:")
    _, logs, _ = ssh_exec(ssh, 'tail -15 /var/www/eims/logs/gunicorn_error.log')
    if logs:
        for line in logs.split('\n')[-5:]:
            if line.strip():
                print(f"  {line}")
        print()
    
    # Final verdict
    print("=" * 70)
    if nginx_code in ['200', '302'] and 'EIMS2026_mysql' in pwd_lines:
        print("✅ SYSTEM IS WORKING!")
        print("\n🌐 Access the login page:")
        print("   http://www.xietongai.com.cn/login/")
        print("   http://39.106.41.239/login/")
    else:
        print("⚠️  Issues detected - see details above")
        print("\n🔧 Recommended actions:")
        if nginx_code not in ['200', '302']:
            print("  1. Restart Gunicorn: pkill -9 gunicorn && cd /var/www/eims && nohup venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application &")
        if 'EIMS2026_mysql' not in pwd_lines:
            print("  2. Fix settings.py password")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    ssh.close()
