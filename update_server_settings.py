import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Updating settings.py on server...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Create a Python script on the server to update settings.py
    update_script = '''#!/usr/bin/env python3.9
import re

settings_path = '/www/wwwroot/EIMS2026/settings.py'

with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Original database config found:")
if 'eims_dingce' in content:
    print("  - Found 'eims_dingce' (will replace)")
if 'root123' in content:
    print("  - Found 'root123' password (will replace)")

# Replace database name
content = content.replace("'NAME': 'eims_dingce'", "'NAME': 'eims'")
# Replace password  
content = content.replace("'PASSWORD': 'root123'", "'PASSWORD': 'EIMS2026_mysql'")

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\\nSettings updated successfully!")
print("New config uses: database='eims', password='EIMS2026_mysql'")
'''
    
    # Write the script to server
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/update_settings.py << \'SCRIPTEOF\'\n{update_script}\nSCRIPTEOF')
    time.sleep(2)
    
    # Execute the script
    print("\nExecuting update script...")
    stdin, stdout, stderr = ssh.exec_command('python3.9 /tmp/update_settings.py')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print(output)
    if error:
        print("Error:", error)
    
    # Verify the changes
    print("\nVerifying changes...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 5 "NAME.*eims" /www/wwwroot/EIMS2026/settings.py | head -10')
    verify_output = stdout.read().decode('utf-8')
    print(verify_output)
    
finally:
    ssh.close()
    print("\nDone!")
