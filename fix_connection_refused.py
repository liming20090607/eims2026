import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Fixing Connection Refused Error")
print("="*80)

# Check Nginx status
print("\n[1] Checking Nginx status...")
stdin, stdout, stderr = ssh.exec_command('systemctl is-active nginx')
nginx_status = stdout.read().decode().strip()
print(f"    Nginx: {nginx_status}")

# Check Gunicorn status
print("\n[2] Checking Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
gunicorn_count = stdout.read().decode().strip()
print(f"    Gunicorn processes: {gunicorn_count}")

# Check if port 80 is listening
print("\n[3] Checking port 80...")
stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep ":80 " || ss -tlnp | grep ":80 "')
port80 = stdout.read().decode().strip()
if port80:
    print(f"    Port 80: LISTENING")
    print(f"    {port80}")
else:
    print("    Port 80: NOT LISTENING")

# Check if port 8000 is listening
print("\n[4] Checking port 8000...")
stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep ":8000 " || ss -tlnp | grep ":8000 "')
port8000 = stdout.read().decode().strip()
if port8000:
    print(f"    Port 8000: LISTENING")
    print(f"    {port8000}")
else:
    print("    Port 8000: NOT LISTENING")

# Start Nginx if not running
if nginx_status != "active":
    print("\n[5] Starting Nginx...")
    stdin, stdout, stderr = ssh.exec_command('systemctl start nginx')
    exit_code = stdout.channel.recv_exit_status()
    if exit_code == 0:
        print("    [OK] Nginx started")
    else:
        print(f"    [FAIL] {stderr.read().decode()}")

# Start Gunicorn if not running
if gunicorn_count == "0" or not gunicorn_count:
    print("\n[6] Starting Gunicorn...")
    gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    gunicorn_count = stdout.read().decode().strip()
    print(f"    Gunicorn processes: {gunicorn_count}")

# Restart Nginx to reload config
print("\n[7] Restarting Nginx...")
stdin, stdout, stderr = ssh.exec_command('systemctl restart nginx')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("    [OK] Nginx restarted")

# Wait for services to be ready
print("\n[8] Waiting for services to stabilize...")
time.sleep(3)

# Test HTTP connection
print("\n[9] Testing HTTP connection...")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_8000 = stdout.read().decode().strip()
print(f"    Port 8000: HTTP {http_8000}")

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/')
http_80 = stdout.read().decode().strip()
print(f"    Port 80: HTTP {http_80}")

# Check firewall
print("\n[10] Checking firewall...")
stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-ports 2>/dev/null || iptables -L -n 2>/dev/null | head -10')
firewall = stdout.read().decode()
if firewall.strip():
    print("    Firewall rules:")
    for line in firewall.split('\n')[:5]:
        print(f"      {line}")

print("\n" + "="*80)
if http_80 in ["200", "302"] or http_8000 in ["200", "302"]:
    print("[SUCCESS] Services are responding!")
    print("="*80)
    print("\nTry accessing: http://www.xietongai.com.cn/")
else:
    print(f"[WARNING] Still not accessible")
    print(f"    Port 80: {http_80}")
    print(f"    Port 8000: {http_8000}")
    print("="*80)
    
    # Check Nginx error log
    print("\nChecking Nginx error log:")
    stdin, stdout, stderr = ssh.exec_command('tail -10 /var/log/nginx/error.log 2>/dev/null')
    nginx_errors = stdout.read().decode()
    if nginx_errors.strip():
        for line in nginx_errors.split('\n')[-5:]:
            if line.strip():
                print(f"  {line}")
    else:
        print("  No recent errors")

print("\n" + "="*80 + "\n")

ssh.close()
