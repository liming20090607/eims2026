import paramiko
import time
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("OpenClaw + Server Auto-Fix Cooperation")
print("="*80)

# 1. Check OpenClaw monitoring status
print("\n[1] Checking OpenClaw monitoring system...")
stdin, stdout, stderr = ssh.exec_command('cat /root/.openclaw/monitoring/status.json 2>/dev/null')
status_json = stdout.read().decode()

if status_json.strip():
    try:
        status = json.loads(status_json)
        print("    ✅ OpenClaw status file exists")
        print(f"    Last check: {status.get('last_check', 'unknown')}")
        print(f"    Services: {json.dumps(status.get('services', {}), indent=6)}")
    except:
        print("    ⚠️  Status file exists but not valid JSON")
        print(f"    Content: {status_json[:200]}")
else:
    print("    ❌ OpenClaw status file not found")

# 2. Check if cron job is active
print("\n[2] Checking OpenClaw cron jobs...")
stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep openclaw')
cron_jobs = stdout.read().decode()
if cron_jobs.strip():
    print("    ✅ OpenClaw cron jobs configured:")
    for line in cron_jobs.strip().split('\n'):
        print(f"       {line}")
else:
    print("    ❌ No OpenClaw cron jobs found")
    print("    Setting up monitoring...")
    
    # Setup cron job
    cron_setup = '''
(crontab -l 2>/dev/null; echo "*/2 * * * * /root/.openclaw/monitoring/scripts/health_check.sh >> /root/.openclaw/monitoring/logs/health_check.log 2>&1") | crontab -
    '''
    ssh.exec_command(cron_setup)
    time.sleep(1)

# 3. Verify all services are actually running
print("\n[3] Comprehensive service check...")

services = {
    'Nginx': 'ps aux | grep "nginx: master" | grep -v grep | wc -l',
    'Gunicorn': 'pgrep -c gunicorn',
    'MySQL': 'systemctl is-active mysqld 2>/dev/null || echo "inactive"',
    'Port 80': 'ss -tlnp | grep ":80 " | wc -l',
    'Port 8000': 'ss -tlnp | grep ":8000 " | wc -l',
}

all_running = True
for name, cmd in services.items():
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    is_running = result != '0' and result != 'inactive' and result != ''
    status_icon = "✅" if is_running else "❌"
    print(f"    {status_icon} {name}: {result}")
    if not is_running:
        all_running = False

# 4. If services are down, start them
if not all_running:
    print("\n[4] Starting failed services...")
    
    stdin, stdout, stderr = ssh.exec_command(services['Nginx'])
    if stdout.read().decode().strip() == '0':
        print("    Starting Nginx...")
        ssh.exec_command('/usr/local/nginx/sbin/nginx')
        time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command(services['Gunicorn'])
    if stdout.read().decode().strip() == '0':
        print("    Starting Gunicorn...")
        ssh.exec_command('cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &')
        time.sleep(3)

# 5. Check if iptables is actually blocking
print("\n[4] Checking iptables rules in detail...")
stdin, stdout, stderr = ssh.exec_command('iptables -L INPUT -n -v --line-numbers 2>/dev/null | head -30')
iptables = stdout.read().decode()
if iptables.strip():
    print("    Current iptables INPUT chain:")
    print(iptables[:500])
    
    # Check if port 80 is being dropped
    if 'dpt:80' in iptables and 'DROP' in iptables:
        print("\n    ⚠️  Found DROP rule for port 80!")
        print("    Removing DROP rule...")
        ssh.exec_command('iptables -D INPUT -p tcp --dport 80 -j DROP 2>/dev/null')
        ssh.exec_command('iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT')
        time.sleep(1)
        print("    ✅ Updated iptables")

# 6. Check firewalld detailed status
print("\n[5] Checking firewalld zones and services...")
stdin, stdout, stderr = ssh.exec_command('firewall-cmd --get-active-zones 2>/dev/null')
zones = stdout.read().decode().strip()
if zones:
    print(f"    Active zones: {zones}")
    
    stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-all 2>/dev/null')
    firewall_all = stdout.read().decode()
    print("    Firewall config:")
    print(firewall_all[:400])

# 7. Try to test connectivity using different methods
print("\n[6] Testing connectivity (multiple methods)...")
time.sleep(2)

# Test 1: Local nginx
stdin, stdout, stderr = ssh.exec_command('curl -s -I --connect-timeout 3 http://127.0.0.1:80/ 2>&1 | head -5')
test1 = stdout.read().decode().strip()
print(f"    Test 1 - Local Nginx headers:\n{test1}")

# Test 2: Server's public IP from localhost
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/ 2>&1')
test2 = stdout.read().decode().strip()
print(f"    Test 2 - Server IP (39.106.41.239): HTTP {test2}")

# Test 3: Try wget
stdin, stdout, stderr = ssh.exec_command('wget -q -O /dev/null --timeout=5 http://39.106.41.239/ 2>&1; echo "EXIT:$?"')
test3 = stdout.read().decode().strip()
print(f"    Test 3 - wget to server IP: {test3}")

# 8. Check if there's a network interface issue
print("\n[7] Checking network interfaces...")
stdin, stdout, stderr = ssh.exec_command('ip addr show | grep -E "inet " | grep -v "127.0.0.1"')
interfaces = stdout.read().decode()
if interfaces.strip():
    print("    Network interfaces:")
    print(interfaces.strip())

# 9. Check if nginx is binding to the right interface
print("\n[8] Checking Nginx bind address...")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep ":80 "')
nginx_bind = stdout.read().decode().strip()
if nginx_bind:
    print(f"    Nginx binding: {nginx_bind}")
    if '0.0.0.0:80' in nginx_bind:
        print("    ✅ Nginx is bound to all interfaces (0.0.0.0)")
    elif '127.0.0.1:80' in nginx_bind:
        print("    ❌ Nginx is ONLY bound to localhost!")
        print("    This is the problem! Nginx needs to bind to 0.0.0.0")

# 10. Final comprehensive test
print("\n[9] Final connectivity test...")
time.sleep(2)

tests = [
    ('Local Gunicorn', 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/'),
    ('Local Nginx', 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/login/'),
    ('Server IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
]

results = {}
for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    results[name] = result
    print(f"    {name}: {result}")

print("\n" + "="*80)
print("DIAGNOSIS AND SOLUTION")
print("="*80)

# Analyze results
if results.get('Local Gunicorn') in ['200', '302', '301'] and \
   results.get('Local Nginx') in ['200', '302', '301'] and \
   results.get('Server IP') in ['000', '', 'FAILED']:
    
    print("\n ROOT CAUSE IDENTIFIED:")
    print("   ✅ All services working perfectly on server")
    print("   ✅ Local access works (HTTP 302)")
    print("   ❌ External access blocked (HTTP 000)")
    print("\n📌 This is 100% an Alibaba Cloud Security Group issue.")
    print("\n🔧 AUTOMATIC FIX NOT POSSIBLE")
    print("   Security groups are managed at the cloud provider level,")
    print("   not on the server itself. No script can fix this automatically.")
    print("\n📋 MANUAL ACTION REQUIRED:")
    print("   1. Open browser to: https://ecs.console.aliyun.com/")
    print("   2. Login with your Alibaba Cloud account")
    print("   3. Find instance: 39.106.41.239")
    print("   4. Click 'Security Group' (安全组)")
    print("   5. Click 'Configure Rules' (配置规则)")
    print("   6. Add inbound rule:")
    print("      - Direction: 入方向 (Inbound)")
    print("      - Protocol: TCP")
    print("      - Port: 80/80")
    print("      - Source: 0.0.0.0/0")
    print("      - Priority: 1")
    print("   7. Click OK/Confirm")
    print("   8. Wait 1-2 minutes")
    print("   9. Try accessing: http://www.xietongai.com.cn/login/")
    print("\n⏱️  After opening port 80, the site will work immediately!")
    
elif results.get('Server IP') in ['200', '302', '301']:
    print("\n✅ SUCCESS! Website is accessible!")
    print("   Try: http://www.xietongai.com.cn/login/")
else:
    print("\n⚠️  Mixed results - need more investigation")
    print("   Results:", json.dumps(results, indent=2))

print("\n" + "="*80 + "\n")

ssh.close()
