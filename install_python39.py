#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Install Python 3.9+ on Alibaba Cloud server with Baota Panel
"""
import paramiko
import time


def main():
    print("=" * 70)
    print("Install Python 3.9+ on Server")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1] Connecting to server...")
        ssh.connect("39.106.41.239", 22, "root", "fjkl546#", timeout=10)
        print("[OK] Connected")
        
        # Check current Python versions
        print("\n[2] Checking available Python versions...")
        stdin, stdout, stderr = ssh.exec_command("python3 --version 2>&1; which python3; ls /usr/bin/python* 2>/dev/null | head -10")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Check if Python 3.9 is already installed via Baota
        print("\n[3] Checking Baota Python installations...")
        stdin, stdout, stderr = ssh.exec_command("ls /www/server/python/ 2>/dev/null || echo 'Baota Python directory not found'")
        output = stdout.read().decode('utf-8').strip()
        print(f"Baota Python dir: {output}")
        
        # Try using Baota's Python installation script
        print("\n[4] Installing Python 3.9 via Baota...")
        print("This may take 10-15 minutes...")
        
        # Method 1: Use Baota's built-in Python installer
        install_cmd = """
        cd /www/server/panel/install
        if [ -f install_soft.sh ]; then
            bash install_soft.sh 0 install python 3.9.18
        else
            echo "Baota install script not found, trying alternative method..."
            # Method 2: Install from source
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
            
            echo "Python 3.9 installed successfully"
        fi
        """
        
        stdin, stdout, stderr = ssh.exec_command(install_cmd, timeout=1800)  # 30 minute timeout
        
        # Monitor installation progress
        print("\nInstallation in progress...")
        start_time = time.time()
        last_check = time.time()
        
        while not stdout.channel.exit_status_ready():
            time.sleep(5)
            elapsed = time.time() - start_time
            
            # Print status every 30 seconds
            if time.time() - last_check > 30:
                print(f"  ... still installing ({int(elapsed)}s elapsed)")
                last_check = time.time()
            
            # Timeout after 25 minutes
            if elapsed > 1500:
                print("[WARN] Installation taking very long, checking status...")
                break
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("\nInstallation output (last 50 lines):")
        lines = output.split('\n')
        if len(lines) > 50:
            print('\n'.join(lines[-50:]))
        else:
            print(output)
        
        if error and "Error" in error:
            print("\nErrors:")
            print(error)
        
        # Verify Python 3.9 installation
        print("\n[5] Verifying Python 3.9 installation...")
        test_commands = [
            "python3.9 --version 2>&1",
            "/usr/local/python39/bin/python3.9 --version 2>&1",
            "which python3.9 2>&1"
        ]
        
        python39_path = None
        for cmd in test_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode('utf-8').strip()
            if output and "3.9" in output:
                print(f"[OK] Found: {cmd} -> {output}")
                if "which" in cmd:
                    python39_path = output
            else:
                error_output = stderr.read().decode('utf-8').strip()
                if error_output:
                    print(f"[INFO] {cmd}: {error_output}")
        
        # If python3.9 not found in standard locations, search for it
        if not python39_path:
            print("\nSearching for Python 3.9 binary...")
            stdin, stdout, stderr = ssh.exec_command("find /usr -name 'python3.9' -type f 2>/dev/null | head -5")
            output = stdout.read().decode('utf-8').strip()
            if output:
                python39_path = output.split('\n')[0]
                print(f"[OK] Found at: {python39_path}")
            else:
                print("[ERROR] Python 3.9 not found!")
                return False
        
        # Create virtual environment with Python 3.9
        print(f"\n[6] Creating new virtual environment with Python 3.9...")
        
        # Remove old venv
        print("Removing old virtual environment...")
        stdin, stdout, stderr = ssh.exec_command("rm -rf /www/wwwroot/EIMS2026/venv")
        time.sleep(2)
        
        # Create new venv
        venv_cmd = f"{python39_path} -m venv /www/wwwroot/EIMS2026/venv"
        print(f"Creating venv: {venv_cmd}")
        stdin, stdout, stderr = ssh.exec_command(venv_cmd, timeout=60)
        time.sleep(5)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error and "Error" in error:
            print(f"[WARN] Venv creation warning: {error}")
        
        # Verify new venv
        print("\n[7] Verifying new virtual environment...")
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/python --version")
        output = stdout.read().decode('utf-8').strip()
        print(f"Venv Python: {output}")
        
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
        output = stdout.read().decode('utf-8').strip()
        print(f"Venv pip: {output}")
        
        # Upgrade pip in new venv
        print("\n[8] Upgrading pip in new venv...")
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip install --upgrade pip", timeout=120)
        time.sleep(15)
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Verify upgraded pip
        stdin, stdout, stderr = ssh.exec_command("/www/wwwroot/EIMS2026/venv/bin/pip --version")
        output = stdout.read().decode('utf-8').strip()
        print(f"Upgraded pip: {output}")
        
        print("\n" + "=" * 70)
        print("Python 3.9 Installation Complete!")
        print("=" * 70)
        print(f"\nNext steps:")
        print(f"1. Run: python fix_pip_and_install.py")
        print(f"   This will install Django 4.2.7 and other dependencies")
        print(f"2. Then run: python auto_deploy.py")
        print(f"   To complete database migration and service restart")
        
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
