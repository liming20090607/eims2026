import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("Checking Connection Refused Issue")
print("="*80)

# Check if Nginx is running
print("\n[1] Checking Nginx...")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
nginx_procs = stdout.read().decode()
if nginx_procs.strip():
    print("    [OK] Nginx is running")
    for line in nginx_procs.split('\n')[:3]:
        print(f"      {line.strip()}")
else:
    print("    [FAIL] Nginx is NOT running")
    print("    Starting Nginx...")
    stdin, stdout, stderr = ssh.exec_command('systemctl start nginx 2>/dev/null || nginx 2>/dev/null || /usr/sbin/nginx')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep | wc -l')
    count = stdout.read().decode().strip()
    print(f"    Nginx processes: {count}")

# Check if Gunicorn is running
print("\n[2] Checking Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
gunicorn_procs = stdout.read().decode()
if gunicorn_procs.strip():
    print("    [OK] Gunicorn is running")
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"    Worker processes: {count}")
else:
    print("    [FAIL] Gunicorn is NOT running")
    print("    Starting Gunicorn...")
    gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"    Worker processes: {count}")

# Check ports
print("\n[3] Checking ports...")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep -E ":(80|8000) "')
ports = stdout.read().decode()
if ports.strip():
    print("    Ports listening:")
    for line in ports.strip().split('\n'):
        print(f"      {line.strip()}")
else:
    print("    [WARNING] No services listening on ports 80 or 8000")

# Test connectivity from server
print("\n[4] Testing HTTP access from server...")
time.sleep(2)

# Test Gunicorn directly
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/ 2>&1')
gunicorn_response = stdout.read().decode().strip()
print(f"    Gunicorn (port 8000): {gunicorn_response}")

# Test Nginx
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/ 2>&1')
nginx_response = stdout.read().decode().strip()
print(f"    Nginx (port 80): {nginx_response}")

# Check firewall
print("\n[5] Checking firewall...")
stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-all 2>/dev/null || echo "firewalld not running"')
firewall = stdout.read().decode()
if 'firewalld not running' in firewall or not firewall.strip():
    # Try iptables
    stdin, stdout, stderr = ssh.exec_command('iptables -L -n 2>/dev/null | grep -E "(ACCEPT|DROP|REJECT)" | head -10 || echo "iptables not configured"')
    iptables = stdout.read().decode()
    if iptables.strip():
        print("    Firewall rules:")
        print(iptables[:300])
    else:
        print("    [OK] No firewall blocking")
else:
    print("    Firewall status:")
    print(firewall[:300])

# Check if port 80 is accessible from outside
print("\n[6] Testing external accessibility...")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/ 2>&1')
external = stdout.read().decode().strip()
print(f"    Server IP (39.106.41.239): HTTP {external}")

print("\n" + "="*80)
if nginx_response in ["200", "302"] or external in ["200", "302"]:
    print("[SUCCESS] Website should be accessible now!")
    print("="*80)
    print("\nTry: http://www.xietongai.com.cn/login/")
elif 'refused' in gunicorn_response.lower() or 'refused' in nginx_response.lower():
    print("[FAIL] Connection still refused")
    print("="*80)
    print("\nPossible issues:")
    print("  1. Services not started properly")
    print("  2. Firewall blocking port 80")
    print("  3. Nginx configuration error")
    print("\nNeed to check Nginx error logs and configuration")
else:
    print(f"[INFO] HTTP Status: {nginx_response or external}")
    print("="*80)

print("\n" + "="*80 + "\n")

ssh.close()
