import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Full System Check and Auto-Fix Trigger")
print("="*80)

# Step 1: Check if Nginx is listening on port 80
print("\n[1] Checking Nginx configuration and status...")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "nginx: master" | grep -v grep')
nginx_master = stdout.read().decode().strip()

if nginx_master:
    print("    ✅ Nginx master process running")
    # Check what port it's listening on
    stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep ":80 "')
    port80 = stdout.read().decode().strip()
    if port80:
        print("    ✅ Port 80 is listening")
    else:
        print("    ❌ Port 80 NOT listening")
        print("    Fixing: Restarting Nginx...")
        ssh.exec_command('pkill nginx; sleep 1; /usr/local/nginx/sbin/nginx')
        time.sleep(2)
else:
    print("    ❌ Nginx not running")
    print("    Starting Nginx...")
    ssh.exec_command('/usr/local/nginx/sbin/nginx')
    time.sleep(2)

# Step 2: Check Nginx config for proper server_name
print("\n[2] Checking Nginx configuration...")
stdin, stdout, stderr = ssh.exec_command('cat /usr/local/nginx/conf/nginx.conf | grep -A 5 "server_name"')
server_config = stdout.read().decode()
print(f"    Current config:\n{server_config[:300]}")

if 'xietongai.com.cn' not in server_config and '_' not in server_config:
    print("    ⚠️  Nginx may not be configured for the domain")
    print("    Fixing: Adding server_name configuration...")
    
    # Create proper nginx config
    nginx_conf = '''server {
    listen 80;
    server_name www.xietongai.com.cn xietongai.com.cn 39.106.41.239 _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/eims/static/;
    }
    
    location /media/ {
        alias /var/www/eims/media/;
    }
}
'''
    
    # Backup and write new config
    ssh.exec_command('cp /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.bak 2>/dev/null')
    stdin, stdout, stderr = ssh.exec_command(f'echo "{nginx_conf}" > /usr/local/nginx/conf/nginx.conf')
    print("    ✅ Nginx configuration updated")
    
    # Restart nginx
    ssh.exec_command('pkill nginx; sleep 1; /usr/local/nginx/sbin/nginx')
    time.sleep(2)

# Step 3: Check Gunicorn
print("\n[3] Checking Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
gunicorn_count = stdout.read().decode().strip()
if gunicorn_count and int(gunicorn_count) > 0:
    print(f"    ✅ Gunicorn running ({gunicorn_count} processes)")
else:
    print("    ❌ Gunicorn not running")
    print("    Starting Gunicorn...")
    gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
    ssh.exec_command(gunicorn_cmd)
    time.sleep(3)

# Step 4: Check if there's a firewall blocking
print("\n[4] Checking firewall status...")
stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-ports 2>/dev/null | grep "80/tcp" || echo "PORT_80_NOT_FOUND"')
firewall = stdout.read().decode().strip()

if 'PORT_80_NOT_FOUND' in firewall:
    print("    ⚠️  Port 80 not in firewall rules")
    print("    Adding port 80 to firewall...")
    ssh.exec_command('firewall-cmd --permanent --add-port=80/tcp 2>/dev/null')
    ssh.exec_command('firewall-cmd --reload 2>/dev/null')
    time.sleep(1)
    print("    ✅ Firewall updated")
else:
    print("    ✅ Port 80 is allowed in firewall")

# Also check iptables directly
stdin, stdout, stderr = ssh.exec_command('iptables -L -n 2>/dev/null | grep "dpt:80" | grep "ACCEPT" || echo "NO_IPTABLES_80"')
iptables = stdout.read().decode().strip()
if 'NO_IPTABLES_80' in iptables:
    print("    ⚠️  iptables may be blocking port 80")
    print("    Adding iptables rule...")
    ssh.exec_command('iptables -I INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null')
    ssh.exec_command('iptables -I INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null')
    time.sleep(1)
    print("    ✅ iptables rules added")

# Step 5: Test connectivity
print("\n[5] Testing connectivity...")
time.sleep(3)

# Test from localhost
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/ 2>&1')
local_test = stdout.read().decode().strip()
print(f"    Local test (127.0.0.1:80): HTTP {local_test}")

# Test from server's own IP
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/ 2>&1')
external_test = stdout.read().decode().strip()
print(f"    External test (39.106.41.239): HTTP {external_test}")

# Test from Gunicorn directly
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/ 2>&1')
gunicorn_test = stdout.read().decode().strip()
print(f"    Gunicorn test (127.0.0.1:8000): HTTP {gunicorn_test}")

# Step 6: Check DNS resolution
print("\n[6] Checking DNS resolution...")
stdin, stdout, stderr = ssh.exec_command('ping -c 1 www.xietongai.com.cn 2>&1 | head -2')
dns = stdout.read().decode()
print(f"    {dns.strip()}")

# Step 7: Check if we can trigger OpenClaw auto-fix
print("\n[7] Checking OpenClaw status...")
stdin, stdout, stderr = ssh.exec_command('ls -la /root/.openclaw/monitoring/scripts/health_check.sh 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"')
openclaw = stdout.read().decode().strip()
if 'EXISTS' in openclaw:
    print("    ✅ OpenClaw monitoring exists")
    
    # Trigger immediate health check
    print("    Triggering OpenClaw health check...")
    ssh.exec_command('bash /root/.openclaw/monitoring/scripts/health_check.sh &')
    time.sleep(2)
    
    # Check status
    stdin, stdout, stderr = ssh.exec_command('cat /root/.openclaw/monitoring/status.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -20')
    status = stdout.read().decode()
    if status.strip():
        print("    Current status:")
        print(status)
else:
    print("    ❌ OpenClaw not found")

print("\n" + "="*80)
print("SUMMARY AND NEXT STEPS")
print("="*80)

if external_test in ['200', '302', '301']:
    print("\n✅ SUCCESS! Website should be accessible now!")
    print("   Try: http://www.xietongai.com.cn/login/")
elif local_test in ['200', '302', '301'] and external_test in ['000', '']:
    print("\n⚠️  PARTIAL SUCCESS:")
    print("   ✅ Server is working (local test passed)")
    print("   ❌ External access still blocked")
    print("\n   This is likely Alibaba Cloud Security Group blocking port 80")
    print("   You need to open port 80 in Alibaba Cloud Console:")
    print("   1. Login to https://ecs.console.aliyun.com/")
    print("   2. Find your instance (39.106.41.239)")
    print("   3. Go to Security Group → Configure Rules")
    print("   4. Add inbound rule: TCP 80/80, Source: 0.0.0.0/0")
else:
    print("\n❌ Services not responding properly")
    print("   Local test:", local_test)
    print("   External test:", external_test)
    print("\n   Check Nginx error log:")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /usr/local/nginx/logs/error.log 2>/dev/null | tail -5')
    print(stdout.read().decode())

print("\n" + "="*80 + "\n")

ssh.close()
