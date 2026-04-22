#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to server...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    print("Connected!\n")
    
    # Use Baota's Python manager to install Python 3.9
    print("Installing Python 3.9 via Baota...")
    cmd = "cd /www/server/panel/install && bash install_soft.sh 0 install python 3.9.18"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=1800)
    
    print("Installation in progress (may take 10-15 minutes)...")
    start_time = time.time()
    
    while not stdout.channel.exit_status_ready():
        time.sleep(10)
        elapsed = int(time.time() - start_time)
        if elapsed % 60 == 0:
            print(f"  ... {elapsed}s elapsed")
        if elapsed > 1200:
            break
    
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print("\nLast 30 lines of output:")
    lines = output.split('\n')
    for line in lines[-30:]:
        print(line)
    
    # Find Python 3.9
    print("\nSearching for Python 3.9...")
    find_cmd = "find /www/server/python -name 'python3.9' -type f 2>/dev/null"
    stdin, stdout, stderr = ssh.exec_command(find_cmd)
    py_path = stdout.read().decode('utf-8').strip()
    
    if py_path:
        print(f"Found: {py_path}")
        
        # Create venv
        print("\nCreating virtual environment...")
        ssh.exec_command("rm -rf /www/wwwroot/EIMS2026/venv")
        time.sleep(2)
        
        venv_cmd = f"{py_path} -m venv /www/wwwroot/EIMS2026/venv"
        stdin, stdout, stderr = ssh.exec_command(venv_cmd, timeout=60)
        time.sleep(5)
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python --version")
        ver = stdout.read().decode('utf-8').strip()
        print(f"Venv Python: {ver}")
        
        # Upgrade pip
        print("\nUpgrading pip...")
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip install --upgrade pip", timeout=120)
        time.sleep(15)
        
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
        pip_ver = stdout.read().decode('utf-8').strip()
        print(f"Pip version: {pip_ver}")
        
        print("\nSUCCESS! Ready to install Django 4.2.7")
    else:
        print("Python 3.9 not found. Installation may have failed.")
        print("Error output:", error[:500] if error else "None")
        
finally:
    ssh.close()
    print("\nDone!")
