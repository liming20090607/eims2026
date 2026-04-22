#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Python 3.9 installation on server
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to server...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    print("Connected!\n")
    
    # Search for Python installations
    print("[1] Searching for Python installations...")
    search_cmds = [
        "find /www -name 'python3.9' -type f 2>/dev/null | head -10",
        "find /usr -name 'python3.9' -type f 2>/dev/null | head -10",
        "ls -la /www/server/panel/pyenv/bin/python* 2>/dev/null",
        "ls -la /www/server/python/*/bin/python* 2>/dev/null",
        "bt 10 2>&1 | head -20"  # Baota menu option 10 shows installed software
    ]
    
    for i, cmd in enumerate(search_cmds, 1):
        print(f"\nSearch {i}: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print(output)
        if error and "No such file" not in error:
            print(f"Error: {error}")
    
    # Check Baota panel version
    print("\n[2] Checking Baota panel info...")
    stdin, stdout, stderr = ssh.exec_command("bt default 2>&1 | head -20")
    output = stdout.read().decode('utf-8')
    print(output)
    
    # List all python binaries
    print("\n[3] All Python binaries on system...")
    stdin, stdout, stderr = ssh.exec_command("find / -name 'python3*' -type f -executable 2>/dev/null | grep -E '(bin|pyenv)' | head -20")
    output = stdout.read().decode('utf-8')
    print(output)
    
finally:
    ssh.close()
    print("\nDone!")
