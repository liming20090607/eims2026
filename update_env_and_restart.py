import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

# Create/update .env file
env_content = """DB_NAME=eims
DB_USER=root
DB_PASSWORD=mysql2026!
DB_HOST=localhost
DB_PORT=3306
"""

print("Creating .env file...")
stdin, stdout, stderr = ssh.exec_command(f"cat > /var/www/eims/.env <<'ENVEOF'\n{env_content}ENVEOF")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("Error:", err)

# Verify
print("\nVerifying .env file...")
stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/.env")
print(stdout.read().decode())

# Restart Gunicorn
print("\nRestarting Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn || true")

import time
time.sleep(2)

ssh.exec_command("cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application")
time.sleep(3)

# Test website
print("\nTesting website...")
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}\\n' http://127.0.0.1:8000/login/")
print(f"HTTP Status: {stdout.read().decode().strip()}")

# Check processes
print("\nChecking Gunicorn processes...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
print(f"Gunicorn processes: {stdout.read().decode().strip()}")

print("\n✅ ALL DONE!")
print("Visit: http://www.xietongai.com.cn/login/")

ssh.close()
