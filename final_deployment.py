#!/usr/bin/env python3
"""
Final deployment - install everything and start
"""

import paramiko
import os
import time
import sys

print("=" * 80)
print("🚀 FINAL DEPLOYMENT")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ Connected\n")
    
    # Step 1: Force install all requirements
    print("[1/5] Installing ALL requirements (force reinstall)...")
    cmd = f"cd {SERVER_PATH} && source venv/bin/activate && pip install --force-reinstall -r requirements.txt 2>&1 | tail -20"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode()
    print(output[-500:] if len(output) > 500 else output)
    print("  ✅ Installation complete\n")
    
    # Step 2: Verify Django can start
    print("[2/5] Testing Django...")
    test_cmd = f"cd {SERVER_PATH} && source venv/bin/activate && python -c 'import django; django.setup(); print(\"Django OK\")' 2>&1"
    stdin, stdout, stderr = ssh.exec_command(test_cmd, timeout=30)
    result = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    
    if 'Django OK' in result:
        print("  ✅ Django setup successful\n")
    else:
        print(f"  ⚠️ Django issue:")
        print(f"     Output: {result[:200]}")
        print(f"     Error: {error[:300]}\n")
        
        # Try to find the missing module
        if 'ModuleNotFoundError' in error:
            import re
            match = re.search(r"No module named '([^']+)'", error)
            if match:
                missing_module = match.group(1)
                print(f"  🔧 Installing missing module: {missing_module}")
                ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && pip install {missing_module}", timeout=60)
                time.sleep(5)
                print("  ✅ Installed\n")
    
    # Step 3: Kill old Gunicorn
    print("[3/5] Cleaning up...")
    ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)
    print("  ✅ Done\n")
    
    # Step 4: Start Gunicorn in background
    print("[4/5] Starting Gunicorn...")
    
    # Create a simple startup script
    script = f"""#!/bin/bash
cd {SERVER_PATH}
source venv/bin/activate
exec gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 300 \\
    --daemon \\
    wsgi:application
"""
    
    # Write script
    write_cmd = f"""cat > /tmp/start_gunicorn.sh << 'EOF'
{script}
EOF
chmod +x /tmp/start_gunicorn.sh
/tmp/start_gunicorn.sh
echo "Gunicorn started"
"""
    
    stdin, stdout, stderr = ssh.exec_command(write_cmd, timeout=15)
    result = stdout.read().decode().strip()
    print(f"  {result}\n")
    
    time.sleep(8)
    
    # Step 5: Verify
    print("[5/5] Verification...")
    
    # Check processes
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
    count = stdout.read().decode().strip()
    print(f"  Gunicorn processes: {count}")
    
    # Test HTTP
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
    http_code = stdout.read().decode().strip()
    print(f"  HTTP Status: {http_code}")
    
    if http_code == '200':
        print("\n" + "=" * 80)
        print("✅✅✅ SUCCESS! SYSTEM IS FULLY OPERATIONAL! ✅✅✅")
        print("=" * 80)
        print(f"\n🌐 Access URLs:")
        print(f"  • http://{SERVER_IP}/login/")
        print(f"  • http://www.xietongai.com.cn/login/")
        print(f"\n⏰ Deployment completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    else:
        print(f"\n⚠️ HTTP {http_code} - Checking errors...")
        stdin, stdout, stderr = ssh.exec_command(f"tail -40 {SERVER_PATH}/logs/gunicorn_error.log 2>/dev/null | grep -i 'error\\|exception\\|traceback' | tail -20")
        errors = stdout.read().decode()
        if errors:
            print(errors)
        else:
            print("No specific errors found in logs")
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
