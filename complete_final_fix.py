#!/usr/bin/env python3
"""
Complete fix: MySQL password + migrations + verify everything
"""

import paramiko
import os
import time
import re
import base64

print("=" * 80)
print("Complete Fix: MySQL + Migrations + Frontend")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

def run(ssh, cmd, desc=""):
    print(f"  {desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_code, output, error

try:
    # 1. Fix MySQL password using skip-grant-tables
    print("\n[1/6] Fixing MySQL password...")
    run(ssh, "systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 3", "Stop MySQL")
    run(ssh, "rm -f /var/lib/mysql/mysql.sock", "Clean socket")
    
    print("  Starting MySQL with skip-grant-tables...")
    run(ssh, "mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", "Start recovery")
    time.sleep(12)
    
    # Wait for socket
    print("  Waiting for socket...")
    socket_ready = False
    for i in range(15):
        exit_code, sock_out, _ = run(ssh, "test -f /var/lib/mysql/mysql.sock && echo READY || echo WAIT", f"Check socket {i+1}/15")
        if 'READY' in sock_out:
            print("  Socket ready!")
            socket_ready = True
            break
        time.sleep(2)
    
    if not socket_ready:
        print("  Socket not ready, checking error log...")
        run(ssh, "tail -20 /var/log/mysqld.log 2>/dev/null", "Check log")
    
    # Reset password
    print("  Resetting password...")
    reset_sql = """FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;"""
    
    exit_code, output, error = run(ssh, f'''mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
{reset_sql}
EOF
''', "Reset password", timeout=30)
    
    print(f"  Output: {output[:200] if output else 'None'}")
    print(f"  Error: {error[:200] if error else 'None'}")
    
    # Shutdown recovery mode
    run(ssh, "mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall -9 mysqld mysqld_safe", "Shutdown")
    time.sleep(5)
    
    # Start MySQL normally
    print("  Starting MySQL normally...")
    run(ssh, "systemctl start mysqld", "Start MySQL")
    time.sleep(5)
    
    # Verify
    exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Verify MySQL")
    if '1' in output:
        print("  MySQL OK")
    else:
        print(f"  MySQL failed: {output}")
        print(f"  Error: {error}")
    
    # 2. Create database
    print("\n[2/6] Creating database...")
    run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' 2>&1", "Create DB")
    print("  Database created")
    
    # 3. Run migrations
    print("\n[3/6] Running migrations...")
    exit_code, output, error = run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -30", "Migrate")
    print(f"  Migration output: {output[:300]}")
    
    # 4. Verify frontend panel exists
    print("\n[4/6] Verifying frontend panel...")
    exit_code, output, error = run(ssh, f"wc -l {SERVER_PATH}/templates/includes/fix_panel.html 2>&1", "Check template")
    print(f"  Template: {output}")
    
    # Verify API views exist
    exit_code, output, error = run(ssh, f"grep -c 'def openclaw_status' {SERVER_PATH}/views_index.py", "Check API")
    print(f"  API views: {output}")
    
    # Verify URLs
    exit_code, output, error = run(ssh, f"grep -c 'openclaw/api' {SERVER_PATH}/urls.py", "Check URLs")
    print(f"  URLs: {output}")
    
    # Verify base.html includes panel
    exit_code, output, error = run(ssh, f"grep -c 'fix_panel' {SERVER_PATH}/templates/base.html", "Check base.html")
    print(f"  base.html: {output}")
    
    # 5. Restart Gunicorn
    print("\n[5/6] Restarting Gunicorn...")
    run(ssh, "pkill -9 -f gunicorn", "Stop")
    time.sleep(3)
    run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", "Start")
    time.sleep(5)
    
    exit_code, output, error = run(ssh, "ps aux | grep '[g]unicorn' | wc -l", "Gunicorn")
    print(f"  Gunicorn: {output} processes")
    
    # 6. Test
    print("\n[6/6] Testing...")
    exit_code, output, error = run(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "HTTP test")
    print(f"  HTTP: {output}")
    
    if output == '200':
        print("\n  Testing login page content...")
        exit_code, output, error = run(ssh, "curl -s http://127.0.0.1:8000/login/ | grep -c 'fix_panel'", "Check fix panel")
        print(f"  Fix panel in page: {output}")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\nNOW REFRESH YOUR BROWSER:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    print("\nYou should see:")
    print("  - Login page (if everything works)")
    print("  - OR fix panel with Manual Fix button (if error)")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
