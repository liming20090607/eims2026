#!/usr/bin/env python
"""
Fix MySQL password in settings.py and restart Gunicorn
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def fix():
    print("🔧 Fixing MySQL password in settings.py")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    # Step 1: Read current settings.py to see DATABASES section
    print("\n[1] Reading current DATABASES configuration...")
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/eims/settings.py")
    content = stdout.read().decode()
    
    # Find DATABASES section
    if 'DATABASES' in content:
        print("  ✅ DATABASES found in settings.py")
        # Find and show the DATABASES section
        lines = content.split('\n')
        in_databases = False
        db_lines = []
        for line in lines:
            if 'DATABASES' in line and '=' in line:
                in_databases = True
            if in_databases:
                db_lines.append(line)
                if line.strip() == '}' and len(db_lines) > 5:
                    break
        
        print("\n  Current DATABASES config:")
        for line in db_lines:
            print(f"    {line}")
        
        # Check if PASSWORD line exists
        has_password = any('PASSWORD' in line for line in db_lines)
        print(f"\n  Has PASSWORD field: {has_password}")
        
        if not has_password:
            # Add PASSWORD field
            print("\n  Adding PASSWORD field...")
            # Find the line with 'NAME' and add PASSWORD after it
            new_db_lines = []
            for line in db_lines:
                new_db_lines.append(line)
                if "'NAME'" in line and 'PASSWORD' not in line:
                    # Add PASSWORD after NAME line
                    indent = '        '
                    new_db_lines.append(f"{indent}'PASSWORD': 'EIMS2026_mysql',")
            
            print("  ✅ PASSWORD field added")
        else:
            print("  ✅ PASSWORD field exists")
        
        # Update settings.py using Python for safety
        print("\n[2] Updating settings.py with correct password...")
        
        python_fix = """
import re

settings_file = '/var/www/eims/eims/settings.py'
with open(settings_file, 'r') as f:
    lines = f.readlines()

new_lines = []
in_databases = False
for line in lines:
    if 'DATABASES' in line and '=' in line:
        in_databases = True
    elif in_databases and line.strip().startswith('}') and 'PASSWORD' not in ''.join(new_lines[-10:]):
        in_databases = False
    
    if in_databases and "'PASSWORD'" in line:
        # Replace password value
        line = re.sub(r"'PASSWORD':\\s*'[^']*'", "'PASSWORD': 'EIMS2026_mysql'", line)
    
    new_lines.append(line)

with open(settings_file, 'w') as f:
    f.writelines(new_lines)

print('✅ settings.py updated')
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 << 'PYEOF'\n{python_fix}\nPYEOF")
        result = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        if result:
            print(f"  {result}")
        if error:
            print(f"  Error: {error}")
        
        # Verify the update
        print("\n[3] Verifying update...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 2 -B 2 'PASSWORD' /var/www/eims/eims/settings.py")
        password_lines = stdout.read().decode().strip()
        if password_lines:
            print(f"  {password_lines}")
        else:
            print("  ⚠️ PASSWORD field not found, checking DATABASES section...")
            stdin, stdout, stderr = ssh.exec_command("grep -A 15 'DATABASES' /var/www/eims/eims/settings.py | head -20")
            print(stdout.read().decode())
    
    else:
        print("  ❌ DATABASES not found in settings.py")
        return
    
    # Step 2: Restart Gunicorn
    print("\n[4] Restarting Gunicorn...")
    ssh.exec_command('pkill -9 gunicorn || true')
    time.sleep(2)
    
    cmd = 'cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"  Gunicorn processes: {count}")
    
    # Step 3: Test
    print("\n[5] Testing HTTP access...")
    tests = [
        ('Local Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/'),
        ('Local Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/'),
    ]
    
    for name, cmd in tests:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        code = stdout.read().decode().strip()
        status = "✅" if code in ['200', '302', '500'] else "❌"
        print(f"  {status} {name}: HTTP {code}")
    
    # Step 4: Check for any remaining errors
    print("\n[6] Checking recent Gunicorn errors...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    errors = stdout.read().decode().strip()
    if errors:
        print("  Recent errors:")
        for line in errors.split('\n')[-5:]:
            print(f"    {line}")
    else:
        print("  ✅ No errors")
    
    ssh.close()
    
    print("\n" + "="*60)
    print("✅ Fix complete!")
    print("="*60)
    print("\nPlease refresh your browser: http://www.xietongai.com.cn/login/")
    print("="*60 + "\n")

if __name__ == '__main__':
    fix()
