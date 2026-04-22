#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import time

def main():
    print("=" * 70)
    print("Setup Python 3.9 Environment and Install Dependencies")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
    print("\n[1] Connecting to server...")
    ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
    print("[OK] Connected")
    
    # Remove old venv
    print("\n[2] Removing old virtual environment...")
    stdin, stdout, stderr = ssh.exec_command("rm -rf /www/wwwroot/EIMS2026/venv")
    time.sleep(2)
    print("[OK] Old venv removed")
    
    # Create new venv with Python 3.9
    print("\n[3] Creating new virtual environment with Python 3.9...")
    stdin, stdout, stderr = ssh.exec_command("/usr/local/python39/bin/python3.9 -m venv /www/wwwroot/EIMS2026/venv", timeout=60)
    time.sleep(5)
    
    # Verify venv
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python --version")
    ver = stdout.read().decode('utf-8').strip()
    print(f"[OK] Venv Python: {ver}")
    
    # Upgrade pip
    print("\n[4] Upgrading pip...")
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip install --upgrade pip", timeout=120)
    time.sleep(15)
    
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
    pip_ver = stdout.read().decode('utf-8').strip()
    print(f"[OK] Pip version: {pip_ver}")
    
    # Check requirements.txt location
    print("\n[5] Checking requirements.txt...")
    stdin, stdout, stderr = ssh.exec_command("find /www/wwwroot/EIMS2026 -maxdepth 2 -name 'requirements.txt' -type f")
    req_path = stdout.read().decode('utf-8').strip()
    print(f"Found: {req_path}")
    
    if not req_path:
        print("[ERROR] requirements.txt not found!")
        return False
    
    # Install dependencies
    print(f"\n[6] Installing dependencies from {req_path}...")
    print("This may take 5-10 minutes...")
    
    cmd = f"/www/wwwroot/EIMS2026/venv/bin/pip install -r {req_path}"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)
    
    start_time = time.time()
    while not stdout.channel.exit_status_ready():
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        if elapsed % 30 == 0 and elapsed > 0:
            print(f"  ... installing ({elapsed}s)")
        if elapsed > 500:
            break
    
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    # Show summary
    lines = output.split('\n')
    success_lines = [l for l in lines if 'Successfully' in l or 'Requirement already' in l]
    
    if success_lines:
        print("\nInstallation summary:")
        for line in success_lines[-10:]:
            print(f"  {line}")
    
    if error and "ERROR" in error:
        print("\nErrors:")
        print(error[:500])
    
    # Verify Django installation
    print("\n[7] Verifying Django installation...")
    stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python -c 'import django; print(django.get_version())'")
    django_ver = stdout.read().decode('utf-8').strip()
    error_out = stderr.read().decode('utf-8')
    
    if django_ver:
        print(f"[OK] Django {django_ver} installed successfully!")
    else:
        print(f"[ERROR] Django installation failed: {error_out}")
        return False
    
    # Verify other key packages
    print("\n[8] Verifying other key packages...")
    packages = ['pymysql', 'pillow', 'whitenoise']
    for pkg in packages:
        stdin, stdout, stderr = ssh.exec_command(f"/www/wwwroot/EIMS2026/venv/bin/python -c 'import {pkg}; print(\"{pkg} OK\")'")
        output = stdout.read().decode('utf-8').strip()
        if output:
            print(f"  [OK] {output}")
        else:
            print(f"  [WARN] {pkg} not found")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Python environment is ready!")
    print("=" * 70)
        print("\nNext step:")
        print("Run: python auto_deploy.py")
        print("This will complete database migration and service restart")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()
        print("\nSSH connection closed")


if __name__ == "__main__":
    main()
