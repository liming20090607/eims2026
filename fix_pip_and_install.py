#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix pip version issue and complete Python dependency installation
"""
import paramiko
import time

print("=" * 70)
print("Fix pip Version and Install Dependencies")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("\n[1] Connecting to server...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    print("[OK] Connected")
    
    # Check Python version
    print("\n[2] Checking Python version...")
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python --version")
    output = stdout.read().decode('utf-8').strip()
    print(f"Python version: {output}")
    
    # Check current pip version
    print("\n[3] Current pip version...")
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
    output = stdout.read().decode('utf-8').strip()
    print(f"Current pip: {output}")
    
    # Upgrade pip
    print("\n[4] Upgrading pip...")
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip install --upgrade pip")
    time.sleep(15)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error and "WARNING" not in error:
        print(error)
    
    # Verify new pip version
    print("\n[5] New pip version...")
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
    output = stdout.read().decode('utf-8').strip()
    print(f"New pip: {output}")
    
    # Check if requirements.txt exists
    print("\n[6] Checking requirements.txt location...")
    stdin, stdout, stderr = ssh.exec_command("find /www/wwwroot/EIMS2026 -maxdepth 2 -name 'requirements.txt' -type f")
    output = stdout.read().decode('utf-8').strip()
    print(f"Found: {output}")
    
    if not output:
        print("[ERROR] requirements.txt not found!")
        print("Listing project directory:")
        stdin, stdout, stderr = ssh.exec_command("ls -la /www/wwwroot/EIMS2026/")
        print(stdout.read().decode('utf-8'))
    else:
        req_file = output.split('\n')[0]
        
        # Install dependencies
        print(f"\n[7] Installing dependencies from {req_file}...")
        print("This may take several minutes...")
        cmd = f"/www/wwwroot/EIMS2026/venv/bin/pip install -r {req_file}"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)
        
        # Monitor progress
        start_time = time.time()
        while not stdout.channel.exit_status_ready():
            time.sleep(2)
            elapsed = time.time() - start_time
            if elapsed > 300:  # 5 minute timeout
                print("[WARN] Installation taking longer than expected...")
                break
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        # Show last 20 lines of output
        lines = output.split('\n')
        if len(lines) > 20:
            print("...\n" + '\n'.join(lines[-20:]))
        else:
            print(output)
        
        if error and "Successfully" not in output:
            print("\nErrors:")
            print(error)
        
        # Verify installation
        print("\n[8] Verifying Django installation...")
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python -c 'import django; print(django.get_version())'")
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8')
        
        if output:
            print(f"[OK] Django {output} installed successfully!")
        else:
            print("[ERROR] Django installation failed")
            print(error)
    
    print("\n" + "=" * 70)
    print("Dependency Installation Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\nSSH connection closed")
