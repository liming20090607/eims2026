#!/usr/bin/env python3
"""
Fix MySQL password after nuclear reset
"""

import paramiko
import os
import time
import re

print("=" * 80)
print("Fix MySQL Password After Reset")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

def run(ssh, cmd, desc=""):
    print(f"  {desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_code, output, error

try:
    # Step 1: Get temp password from log
    print("\n[1/4] Getting temporary password...")
    exit_code, log_output, error = run(ssh, "cat /var/log/mysqld.log 2>/dev/null | grep -i 'temporary password' | tail -1", "Read log")
    
    if log_output:
        print(f"  Log line: {log_output[:100]}")
        match = re.search(r'root@localhost:\s*(\S+)', log_output)
        if match:
            temp_pass = match.group(1)
            print(f"  Temp password found: {temp_pass[:10]}...")
        else:
            print("  Could not parse password")
            # Try to find it another way
            run(ssh, "grep -A 2 -B 2 'password' /var/log/mysqld.log | tail -10", "Search log")
            sys.exit(1)
    else:
        print("  No log file or no password found")
        # Try alternative: start with skip-grant-tables
        print("  Trying skip-grant-tables method...")
        run(ssh, "systemctl stop mysqld; killall -9 mysqld 2>/dev/null; sleep 3", "Stop MySQL")
        
        # Start with skip-grant-tables
        run(ssh, "mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", "Start skip-grant")
        time.sleep(10)
        
        # Check socket
        for i in range(10):
            exit_code, sock_out, _ = run(ssh, "ls /var/lib/mysql/mysql.sock 2>&1", f"Check socket {i+1}")
            if 'mysql.sock' in sock_out:
                print("  Socket ready")
                break
            time.sleep(2)
        
        # Reset password
        print("\n[2/4] Resetting password...")
        reset_sql = "FLUSH PRIVILEGES; ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql'; FLUSH PRIVILEGES;"
        exit_code, output, error = run(ssh, f'mysql -u root --socket=/var/lib/mysql/mysql.sock -e "{reset_sql}" 2>&1', "Reset")
        
        # Shutdown
        run(ssh, "mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld", "Shutdown")
        time.sleep(3)
        
        # Start normally
        print("\n[3/4] Starting MySQL normally...")
        run(ssh, "systemctl start mysqld", "Start MySQL")
        time.sleep(5)
        
        # Verify
        print("\n[4/4] Verifying...")
        exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Verify")
        if '1' in output:
            print("  MySQL OK with password EIMS2026_mysql")
        else:
            print(f"  Failed: {output}")
        
        # Create database
        run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' 2>&1", "Create DB")
        print("  Database ready")
    else:
        # Use temp password to change
        print("\n[2/4] Changing password with temp password...")
        change_cmd = f'mysql -uroot -p"{temp_pass}" --connect-expired-password -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\'; FLUSH PRIVILEGES;" 2>&1'
        exit_code, output, error = run(ssh, change_cmd, "Change password")
        
        if exit_code != 0:
            print(f"  Failed: {error[:200]}")
            # Try alternate method
            print("  Trying alternate method...")
            run(ssh, f'mysql -uroot -p{temp_pass} --connect-expired-password -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\';" 2>&1', "Alternate")
        
        # Verify
        print("\n[3/4] Verifying new password...")
        exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Verify")
        if '1' in output:
            print("  MySQL OK")
        else:
            print(f"  Verification failed: {output}")
        
        # Create database
        print("\n[4/4] Creating database...")
        run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' 2>&1", "Create DB")
        print("  Database ready")
    
    print("\n" + "=" * 80)
    print("MySQL Password Fixed")
    print("=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
