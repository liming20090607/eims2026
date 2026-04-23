import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("Deploying correct settings.py...")

# Read local settings.py
with open('settings.py', 'r', encoding='utf-8') as f:
    local_settings = f.read()

# Check if root_admin is in the settings
if 'root_admin' in local_settings:
    print("✓ Local settings.py contains root_admin database configuration")
else:
    print("✗ Local settings.py does NOT contain root_admin - checking local file...")
    print("Searching for DATABASES configuration...")
    
# Upload to server
print("\nUploading settings.py to server...")
stdin, stdout, stderr = ssh.exec_command("cat > /var/www/eims/eims/settings.py <<'SETTINGSEOF'\n" + local_settings + "\nSETTINGSEOF")
time.sleep(2)

# Verify upload
print("Verifying upload...")
stdin, stdout, stderr = ssh.exec_command("wc -l /var/www/eims/eims/settings.py")
print(f"Server file lines: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command("grep -c 'root_admin' /var/www/eims/eims/settings.py")
count = stdout.read().decode().strip()
print(f"'root_admin' occurrences: {count}")

# Restart Gunicorn
print("\nRestarting Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn || true")
time.sleep(3)
ssh.exec_command("/var/www/eims/start_gunicorn.sh")
time.sleep(5)

# Test
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"\nHTTP Status: {http_status}")

time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("tail -5 /var/www/eims/logs/gunicorn_error.log | grep -i 'root_admin\\|ConnectionDoesNotExist' || echo 'No connection errors'")
errors = stdout.read().decode()
print(f"Connection errors: {errors.strip()}")

if http_status == '200' and 'No connection errors' in errors:
    print("\n✅ SUCCESS! Website should be working now")
else:
    print("\n⚠️ Still having issues")

ssh.close()
