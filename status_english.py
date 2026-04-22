import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("\n" + "="*80)
print("SYSTEM STATUS REPORT")
print("="*80)

# 1. MySQL Status
print("\n[1] MySQL Database:")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null && echo "CONNECTED" || echo "FAILED"')
mysql_status = stdout.read().decode().strip()
if "CONNECTED" in mysql_status:
    print("    [OK] MySQL is connected")
else:
    print("    [FAIL] MySQL connection failed")

# 2. Gunicorn Status
print("\n[2] Gunicorn Application Server:")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn 2>/dev/null')
gunicorn_count = stdout.read().decode().strip()
if gunicorn_count and int(gunicorn_count) > 0:
    print(f"    [OK] Running ({gunicorn_count} workers)")
else:
    print("    [FAIL] Not running")

# 3. Nginx Status
print("\n[3] Nginx Reverse Proxy:")
stdin, stdout, stderr = ssh.exec_command('pgrep nginx >/dev/null 2>&1 && echo "RUNNING" || echo "STOPPED"')
nginx_status = stdout.read().decode().strip()
if "RUNNING" in nginx_status:
    print("    [OK] Nginx is running")
else:
    print("    [FAIL] Nginx is stopped")

# 4. HTTP Test
print("\n[4] Website Access Test:")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_code = stdout.read().decode().strip()
if http_code == "200":
    print(f"    [OK] HTTP {http_code} - Website is accessible")
elif http_code == "302":
    print(f"    [OK] HTTP {http_code} - Redirect (normal)")
elif http_code == "500":
    print(f"    [WARN] HTTP {http_code} - Server error")
else:
    print(f"    [FAIL] HTTP {http_code}")

# 5. Auto-Fix System
print("\n[5] OpenClaw Auto-Fix System:")
stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep "openclaw.*health_check" | head -1')
cron_config = stdout.read().decode().strip()
if cron_config:
    print("    [OK] Scheduled task configured")
    print(f"         {cron_config}")
else:
    print("    [FAIL] Not configured")

# 6. Recent Auto-Fix Activity
print("\n[6] Recent Auto-Fix Activity:")
stdin, stdout, stderr = ssh.exec_command('tail -15 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | grep -E "\\[.*%\\]|==========" | tail -15')
log_output = stdout.read().decode().strip()
if log_output:
    for line in log_output.split('\n'):
        if line.strip():
            # Remove Chinese characters to avoid encoding issues
            clean_line = ''.join(char for char in line if ord(char) < 128 or char in ['%', '[', ']', ':', '-', ' ', '.', '/', '\\'])
            if clean_line.strip():
                print(f"    {clean_line}")
else:
    print("    [INFO] No auto-fix activity (system is stable)")

# 7. Health Check Log
print("\n[7] Recent Health Checks:")
stdin, stdout, stderr = ssh.exec_command('tail -8 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null | grep "%" | tail -5')
health_log = stdout.read().decode().strip()
if health_log:
    for line in health_log.split('\n'):
        if line.strip():
            clean_line = ''.join(char for char in line if ord(char) < 128 or char in ['%', '[', ']', ':', '-', ' ', '.', '/', '\\'])
            if clean_line.strip():
                print(f"    {clean_line}")
else:
    print("    [INFO] No health check records yet")

print("\n" + "="*80)
print("SUMMARY AND RECOMMENDATIONS")
print("="*80)

# Determine overall status
all_good = (
    "CONNECTED" in mysql_status and 
    gunicorn_count and int(gunicorn_count) > 0 and 
    "RUNNING" in nginx_status and
    http_code in ["200", "302"]
)

if all_good:
    print("\n[SUCCESS] All services are running normally!")
    print("\nYou can now:")
    print("  - Visit: http://www.xietongai.com.cn/login/")
    print("  - Try logging into the system")
    print("  - Auto-fix will repair MySQL within 2 minutes if it fails again")
else:
    print("\n[WARNING] Some services have issues.")
    if http_code == "500":
        print("\nThe website is returning HTTP 500 error.")
        print("This is likely because MySQL keeps crashing.")
        print("\nRecommended action:")
        print("  Run: python e:\\EIMS2026\\emergency_fix_crash.py")

print("\nTo view real-time progress bars:")
print("  SSH to server and run:")
print("  tail -f /root/.openclaw/monitoring/logs/auto_fix.log")

print("\n" + "="*80 + "\n")

ssh.close()
