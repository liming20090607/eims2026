#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify MySQL connection and check database status on server
"""
import paramiko
import time

# Server configuration
SSH_HOST = "39.106.41.239"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "fjkl546#"
MYSQL_PASSWORD = "EIMS2026_mysql"

def main():
    print("=" * 70)
    print("MySQL Status Verification")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD, timeout=10)
        print("[OK] Connected successfully")
        
        # Check MySQL service status
        print("\n[2] Checking MySQL service status...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status mysqld | head -20")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Test MySQL connection with new password
        print("\n[3] Testing MySQL connection with password...")
        test_cmd = "mysql -uroot -p{} -e 'SELECT VERSION() AS mysql_version; SELECT NOW() AS current_time;'".format(MYSQL_PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print("[OK] MySQL connection successful!")
            print(output)
        else:
            print("[ERROR] Connection failed:")
            print(error)
        
        # List databases
        print("\n[4] Listing databases...")
        db_cmd = "mysql -uroot -p{} -e 'SHOW DATABASES;'".format(MYSQL_PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(db_cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print("[OK] Databases:")
            print(output)
        else:
            print("[ERROR] Failed to list databases:")
            print(error)
        
        # Check if EIMS database exists
        print("\n[5] Checking for EIMS database...")
        check_cmd = "mysql -uroot -p{} -e \"SELECT COUNT(*) AS db_exists FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='eims';\"".format(MYSQL_PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if "1" in output:
            print("[OK] EIMS database exists")
        else:
            print("[INFO] EIMS database does not exist yet (normal for fresh deployment)")
        
        print("\n" + "=" * 70)
        print("Verification Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
    finally:
        ssh.close()
        print("\nSSH connection closed")

if __name__ == "__main__":
    main()
