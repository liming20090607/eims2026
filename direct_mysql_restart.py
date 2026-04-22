#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct MySQL restart via systemctl
"""
import paramiko
import time

print("=" * 70)
print("MySQL Direct Restart")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("\n[1] Connecting...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    print("[OK] Connected")
    
    # Force kill any existing MySQL processes
    print("\n[2] Killing MySQL processes...")
    stdin, stdout, stderr = ssh.exec_command("pkill -9 mysqld; sleep 2")
    time.sleep(3)
    print("[OK] Processes killed")
    
    # Start MySQL
    print("\n[3] Starting MySQL...")
    stdin, stdout, stderr = ssh.exec_command("systemctl start mysqld")
    time.sleep(8)
    print("[OK] Start command sent")
    
    # Check status
    print("\n[4] Checking status...")
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active mysqld")
    status = stdout.read().decode('utf-8').strip()
    print(f"Service status: {status}")
    
    # Test connection
    print("\n[5] Testing connection...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1;'")
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output and "1" in output:
        print("[OK] MySQL is working!")
        print(output)
    else:
        print("[ERROR] Connection failed")
        print(error)
        
except Exception as e:
    print(f"\n[ERROR] {e}")
finally:
    ssh.close()
    print("\nDone!")
