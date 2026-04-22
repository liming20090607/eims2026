#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Restart MySQL service properly and verify it's running
"""
import paramiko
import time

# Server configuration
SSH_HOST = "39.106.41.239"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "fjkl546#"
MYSQL_PASSWORD = "EIMS2026_mysql"

def exec_command(ssh, cmd, timeout=30):
    """Execute command and return status, output, error"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    status = stdout.channel.recv_exit_status()
    return status, output, error

def main():
    print("=" * 70)
    print("MySQL Service Restart")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD, timeout=10)
        print("[OK] Connected successfully")
        
        # Stop MySQL first
        print("\n[2] Stopping MySQL service...")
        status, output, error = exec_command(ssh, "systemctl stop mysqld", timeout=30)
        time.sleep(3)
        if status == 0 or "failed" not in output.lower():
            print("[OK] MySQL stopped")
        else:
            print("[WARN] Stop warning: {}".format(error))
        
        # Start MySQL
        print("\n[3] Starting MySQL service...")
        status, output, error = exec_command(ssh, "systemctl start mysqld", timeout=30)
        time.sleep(5)
        
        if status == 0:
            print("[OK] MySQL started successfully")
        else:
            print("[ERROR] Failed to start MySQL:")
            print(error)
            return
        
        # Check service status
        print("\n[4] Checking MySQL service status...")
        status, output, error = exec_command(ssh, "systemctl status mysqld | head -15", timeout=10)
        print(output)
        
        # Test connection
        print("\n[5] Testing MySQL connection...")
        test_cmd = "mysql -uroot -p{} -e 'SELECT VERSION() AS mysql_version; SELECT NOW() AS current_time;'".format(MYSQL_PASSWORD)
        status, output, error = exec_command(ssh, test_cmd, timeout=10)
        
        if status == 0 and output:
            print("[OK] MySQL connection successful!")
            print(output)
        else:
            print("[ERROR] Connection test failed:")
            print(error)
            return
        
        # List databases
        print("\n[6] Listing databases...")
        db_cmd = "mysql -uroot -p{} -e 'SHOW DATABASES;'".format(MYSQL_PASSWORD)
        status, output, error = exec_command(ssh, db_cmd, timeout=10)
        
        if status == 0 and output:
            print("[OK] Databases:")
            print(output)
        else:
            print("[ERROR] Failed to list databases:")
            print(error)
        
        print("\n" + "=" * 70)
        print("MySQL Service Restart Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
    finally:
        ssh.close()
        print("\nSSH connection closed")

if __name__ == "__main__":
    main()
