import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("\n" + "="*80)
print("当前状态")
print("="*80)

# MySQL
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null && echo OK || echo FAIL')
print(f"MySQL: {stdout.read().decode().strip()}")

# Gunicorn
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
count = stdout.read().decode().strip()
print(f"Gunicorn: {count} workers")

# HTTP
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
code = stdout.read().decode().strip()
print(f"HTTP: {code}")

# Latest auto-fix
print("\n最近自动修复:")
stdin, stdout, stderr = ssh.exec_command('tail -5 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | grep "%"')
for line in stdout.read().decode().strip().split('\n'):
    if line:
        print(f"  {line}")

print("\n" + "="*80)
if code == "200":
    print("✅ 网站可以访问了！")
else:
    print(f"⚠️  HTTP状态: {code}")
print("="*80 + "\n")

ssh.close()
