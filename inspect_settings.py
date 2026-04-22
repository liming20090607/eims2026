#!/usr/bin/env python
"""
检查settings.py内容
"""

import paramiko

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

# Check if settings.py exists
stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/eims/eims/settings.py")
print("File info:", stdout.read().decode().strip())

# Read settings.py
stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/eims/settings.py")
content = stdout.read().decode()

print("\n" + "="*60)
print("SETTINGS.PY CONTENT:")
print("="*60)

# Check for DATABASES
if 'DATABASE' in content:
    print("\n✅ Found DATABASE keyword")
    # Find DATABASE section
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'DATABASE' in line:
            print(f"\nLine {i}: {line}")
            # Show context
            for j in range(max(0, i-1), min(len(lines), i+15)):
                print(f"{j+1}: {lines[j]}")
else:
    print("\n❌ DATABASE keyword not found!")
    print("\nLast 50 lines of settings.py:")
    lines = content.split('\n')
    for line in lines[-50:]:
        print(line)

ssh.close()
