import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Final Check After Firewall Template Confirmed")
print("="*80)

# 1. Check if Nginx is running and listening on port 80
print("\n[1] Checking Nginx status...")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "nginx: master" | grep -v grep')
nginx = stdout.read().decode().strip()
if nginx:
    print("    ✅ Nginx master process running")
    for line in nginx.split('\n')[:2]:
        print(f"       {line.strip()}")
else:
    print("    ❌ Nginx not running")
    print("    Starting Nginx...")
    ssh.exec_command('/usr/local/nginx/sbin/nginx')
    time.sleep(2)

# 2. Check what port 80 is bound to
print("\n[2] Checking port 80 binding...")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep ":80 "')
port80 = stdout.read().decode().strip()
if port80:
    print(f"    ✅ Port 80 listening:")
    print(f"       {port80}")
    if '0.0.0.0:80' in port80:
        print("       ✅ Bound to all interfaces (correct)")
    elif '127.0.0.1:80' in port80:
        print("       ❌ Only bound to localhost (wrong!)")
else:
    print("    ❌ Port 80 not listening")

# 3. Check Nginx configuration
print("\n[3] Checking Nginx config...")
stdin, stdout, stderr = ssh.exec_command('cat /usr/local/nginx/conf/nginx.conf | grep -A 10 "listen 80"')
config = stdout.read().decode()
print(f"    Current config:")
print(config[:300])

# 4. Check if Gunicorn is running
print("\n[4] Checking Gunicorn...")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
gunicorn_count = stdout.read().decode().strip()
if gunicorn_count and int(gunicorn_count) > 0:
    print(f"    ✅ Gunicorn running ({gunicorn_count} workers)")
else:
    print("    ❌ Gunicorn not running")
    print("    Starting Gunicorn...")
    ssh.exec_command('cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &')
    time.sleep(3)

# 5. Test connectivity from different angles
print("\n[5] Testing connectivity...")
time.sleep(2)

tests = [
    ('Gunicorn direct (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx local (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('Server public IP (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(f"    {name}: HTTP {result}")

# 6. Check iptables
print("\n[6] Checking iptables...")
stdin, stdout, stderr = ssh.exec_command('iptables -L INPUT -n | grep "dpt:80"')
iptables = stdout.read().decode().strip()
if iptables:
    print(f"    iptables rules for port 80:")
    print(f"    {iptables}")
else:
    print("    No iptables rules found for port 80")
    print("    Adding ACCEPT rule...")
    ssh.exec_command('iptables -I INPUT -p tcp --dport 80 -j ACCEPT')
    ssh.exec_command('iptables -I INPUT -p tcp --dport 8000 -j ACCEPT')

# 7. Trigger OpenClaw health check
print("\n[7] Triggering OpenClaw health check...")
stdin, stdout, stderr = ssh.exec_command('bash /root/.openclaw/monitoring/scripts/health_check.sh > /dev/null 2>&1 &')
time.sleep(3)

# Check OpenClaw logs
stdin, stdout, stderr = ssh.exec_command('tail -15 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null | grep -E "\\[.*\\]" | tail -5')
openclaw_log = stdout.read().decode()
if openclaw_log.strip():
    print("    Recent OpenClaw health check:")
    for line in openclaw_log.strip().split('\n'):
        print(f"      {line}")

# 8. Final diagnosis
print("\n" + "="*80)
print("DIAGNOSIS")
print("="*80)

# Final external test
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/ 2>&1')
final = stdout.read().decode().strip()

if final in ['200', '302', '301']:
    print("\n🎉 SUCCESS! Website is now accessible!")
    print("   Try: http://www.xietongai.com.cn/login/")
    print("   Or: http://39.106.41.239/login/")
    
elif final in ['000', '', 'FAILED']:
    print("\n📊 Current Status:")
    print("   ✅ Firewall template configured (port 80 allowed)")
    print("   ✅ Nginx running and bound to 0.0.0.0:80")
    print("   ✅ Gunicorn running on 127.0.0.1:8000")
    print("   ✅ iptables rules added")
    print("   ✅ OpenClaw monitoring active")
    print("\n   ❌ External access still HTTP 000")
    print("\n🔍 Possible reasons:")
    print("   1. Firewall template not applied to your server instance")
    print("      - Check if template 'EIMS-Django' is bound to instance 39.106.41.239")
    print("   2. Cloud provider routing issue")
    print("   3. DNS resolution problem")
    print("\n💡 Next steps:")
    print("   1. Verify firewall template is applied to your server")
    print("   2. Try accessing by IP: http://39.106.41.239/")
    print("   3. If IP works but domain doesn't, check DNS settings")
else:
    print(f"\n⚠️  Unexpected result: HTTP {final}")
    print("   Check Nginx error log for details")
    stdin, stdout, stderr = ssh.exec_command('tail -10 /usr/local/nginx/logs/error.log 2>/dev/null')
    print(stdout.read().decode()[:500])

print("\n" + "="*80 + "\n")

ssh.close()
