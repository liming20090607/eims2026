#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Installing Python 3.9 from source...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    
    # Install dependencies and compile Python 3.9
    cmd = """
    yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make
    
    cd /tmp
    wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
    tar xzf Python-3.9.18.tgz
    cd Python-3.9.18
    ./configure --enable-optimizations --prefix=/usr/local/python39
    make -j$(nproc)
    make altinstall
    
    ln -sf /usr/local/python39/bin/python3.9 /usr/bin/python3.9
    ln -sf /usr/local/python39/bin/pip3.9 /usr/bin/pip3.9
    
    python3.9 --version
    echo "Installation complete"
    """
    
    print("This will take 15-20 minutes...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=2400)
    
    start_time = time.time()
    while not stdout.channel.exit_status_ready():
        time.sleep(15)
        elapsed = int(time.time() - start_time)
        if elapsed % 60 == 0:
            print(f"  ... {elapsed}s elapsed")
        if elapsed > 1800:
            break
    
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print("\nOutput (last 20 lines):")
    lines = output.split('\n')
    for line in lines[-20:]:
        print(line)
    
    if error:
        print("\nErrors:", error[:300])
    
    # Verify
    print("\nVerifying...")
    stdin, stdout, stderr = ssh.exec_command("python3.9 --version")
    ver = stdout.read().decode('utf-8').strip()
    print(f"Python version: {ver}")
    
    if "3.9" in ver:
        print("\nCreating venv...")
        ssh.exec_command("rm -rf /www/wwwroot/EIMS2026/venv")
        time.sleep(2)
        
        ssh.exec_command("python3.9 -m venv /www/wwwroot/EIMS2026/venv", timeout=60)
        time.sleep(5)
        
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python --version")
        venv_ver = stdout.read().decode('utf-8').strip()
        print(f"Venv Python: {venv_ver}")
        
        print("\nUpgrading pip...")
        ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip install --upgrade pip", timeout=120)
        time.sleep(15)
        
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
        pip_ver = stdout.read().decode('utf-8').strip()
        print(f"Pip: {pip_ver}")
        
        print("\nSUCCESS!")
    else:
        print("Installation failed")
        
finally:
    ssh.close()
    print("Done!")
