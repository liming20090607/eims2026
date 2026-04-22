#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Checking Python 3.9 installation status...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    
    # Check if python3.9 exists
    checks = [
        "python3.9 --version 2>&1",
        "/usr/local/python39/bin/python3.9 --version 2>&1",
        "ls -la /usr/local/python39/bin/python* 2>&1 | head -10",
        "find /tmp -name 'Python-3.9*' -type d 2>/dev/null"
    ]
    
    for cmd in checks:
        print(f"\n{cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if output:
            print(output)
        if error and "No such file" not in error:
            print(f"Error: {error[:200]}")
    
finally:
    ssh.close()
    print("\nDone!")
