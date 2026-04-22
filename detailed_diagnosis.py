import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("详细诊断")
print("="*80)

# 1. Gunicorn进程
print("\n【1】Gunicorn进程详情:")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
processes = stdout.read().decode()
if processes.strip():
    for line in processes.split('\n')[:6]:
        print(f"  {line}")
else:
    print("  ❌ Gunicorn未运行")

# 2. 测试Gunicorn端口
print("\n【2】测试Gunicorn端口 (8000):")
stdin, stdout, stderr = ssh.exec_command('curl -v http://127.0.0.1:8000/login/ 2>&1 | head -30')
result = stdout.read().decode()
print(result if result.strip() else "  (无响应)")

# 3. Django数据库测试
print("\n【3】Django数据库连接测试:")
django_test = '''cd /var/www/eims && source venv/bin/activate && python3 << 'EOF'
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')

try:
    import django
    django.setup()
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"✅ 成功: {count} users")
except Exception as e:
    print(f"❌ 错误: {e}")
EOF
'''
stdin, stdout, stderr = ssh.exec_command(django_test)
time.sleep(3)
output = stdout.read().decode() + stderr.read().decode()
for line in output.split('\n'):
    if line.strip() and 'Warning' not in line:
        print(f"  {line}")

# 4. 检查settings.py中的数据库配置
print("\n【4】数据库配置:")
stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES.*=" /var/www/eims/settings.py | head -15')
db_config = stdout.read().decode()
print(db_config if db_config.strip() else "  (无法读取)")

# 5. MySQL服务状态
print("\n【5】MySQL服务状态:")
stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld && echo Active || echo Inactive')
status = stdout.read().decode().strip()
print(f"  {status}")

# 6. MySQL进程
print("\n【6】MySQL进程:")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysqld | grep -v grep | head -3')
mysql_procs = stdout.read().decode()
if mysql_procs.strip():
    for line in mysql_procs.split('\n')[:3]:
        print(f"  {line}")
else:
    print("  ❌ MySQL未运行")

print("\n" + "="*80)

ssh.close()
