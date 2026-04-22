import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Final Status Check")
print("="*80)

# Check Gunicorn
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
print(f"\nGunicorn processes: {count}")

# Test HTTP
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
gunicorn_status = stdout.read().decode().strip()
print(f"Gunicorn (8000): HTTP {gunicorn_status}")

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
nginx_status = stdout.read().decode().strip()
print(f"Nginx (80): HTTP {nginx_status}")

# Test external
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/')
external_status = stdout.read().decode().strip()
print(f"External IP (80): HTTP {external_status}")

# Check error logs
if gunicorn_status == '500' or nginx_status == '500':
    print("\nError log:")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    print(stdout.read().decode()[-500:])
else:
    print("\n✅ Website is working!")
    print("Try: http://39.106.41.239/login/")

ssh.close()
