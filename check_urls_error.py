import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("Checking server's urls.py...")
print("="*60)

# Read the urls.py file on the server
stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/urls.py')
server_urls = stdout.read().decode()

print("Server urls.py content:")
print(server_urls[:1000])

# Look for openclaw_status
print("\n\nSearching for openclaw_status reference:")
stdin, stdout, stderr = ssh.exec_command('grep -n "openclaw_status" /var/www/eims/urls.py')
openclaw_refs = stdout.read().decode().strip()
if openclaw_refs:
    print(f"Found references:\n{openclaw_refs}")
else:
    print("No openclaw_status reference found")

# Check if views_index has openclaw_status
print("\n\nChecking views_index for openclaw_status:")
stdin, stdout, stderr = ssh.exec_command('grep -n "openclaw_status" /var/www/eims/eims_app/views/views_index.py')
views_refs = stdout.read().decode().strip()
if views_refs:
    print(f"Found in views:\n{views_refs}")
else:
    print("Function not defined in views_index.py")

ssh.close()
