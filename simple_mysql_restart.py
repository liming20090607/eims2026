#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple MySQL restart and verification
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to server...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    print("Connected!\n")
    
    # Restart MySQL using Baota command
    print("Restarting MySQL service via Baota...")
    stdin, stdout, stderr = ssh.exec_command("bt 16")
    time.sleep(10)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("Error:", error)
    
    # Wait for MySQL to start
    print("\nWaiting for MySQL to start...")
    time.sleep(5)
    
    # Test connection
    print("\nTesting MySQL connection...")
    test_cmd = "mysql -uroot -pEIMS2026_mysql -e 'SELECT VERSION();'"
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output:
        print("✓ MySQL is running!")
        print(output)
    else:
        print("✗ Connection failed:")
        print(error)
        
finally:
    ssh.close()
    print("\nDone!")
