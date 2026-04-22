import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("Finding views_index.py...")
stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "views_index.py" 2>/dev/null')
result = stdout.read().decode().strip()
print(f"Found: {result}")

if result:
    # Get the directory
    import os
    dir_path = os.path.dirname(result)
    rel_path = result.replace('/var/www/eims/', '').replace('/views_index.py', '')
    print(f"Relative path: {rel_path}")
    
    # Fix urls.py with correct import
    print("\nFixing urls.py...")
    fix_cmd = f"sed -i 's|from eims_app import views_index|from {rel_path.replace('/', '.')} import views_index|' /var/www/eims/urls.py"
    stdin, stdout, stderr = ssh.exec_command(fix_cmd)
    exit_code = stdout.channel.recv_exit_status()
    
    if exit_code == 0:
        print("[OK] Fixed")
        stdin, stdout, stderr = ssh.exec_command('grep "views_index" /var/www/eims/urls.py | head -1')
        verify = stdout.read().decode().strip()
        print(f"New import: {verify}")
else:
    print("views_index.py not found!")
    print("\nChecking what files exist in eims_app/views/...")
    stdin, stdout, stderr = ssh.exec_command('ls /var/www/eims/eims_app/views/ | grep -i index')
    files = stdout.read().decode().strip()
    print(files if files else "No index files found")

ssh.close()
