#!/usr/bin/env python
"""
快速状态检查
"""

import paramiko

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

print("\n📊 当前状态:\n")

# 服务状态
for name, cmd in [('MySQL', 'systemctl is-active mysqld'), ('Gunicorn', 'pgrep -c gunicorn || echo 0'), ('Nginx', 'pgrep -c nginx || echo 0')]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    icon = "✅" if result not in ['0', 'inactive', ''] else "❌"
    print(f"  {icon} {name}: {result}")

# HTTP测试
print("\nHTTP测试:")
for name, cmd in [('8000', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/'), ('80', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/')]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302'] else "❌"
    print(f"  {icon} 端口{name}: HTTP {code}")

# 错误日志
print("\n最新错误:")
stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
errors = stdout.read().decode().strip()
if errors:
    for line in errors.split('\n')[-3:]:
        print(f"  {line[:70]}")
else:
    print("  (无)")

ssh.close()
print()
