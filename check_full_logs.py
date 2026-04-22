import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("完整自动修复日志")
print("="*80)

stdin, stdout, stderr = ssh.exec_command('cat /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | tail -50')
log = stdout.read().decode()
print(log)

print("\n" + "="*80)
print("Gunicorn日志")
print("="*80)

stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/gunicorn.log 2>/dev/null')
gunicorn_log = stdout.read().decode()
print(gunicorn_log if gunicorn_log.strip() else "(无日志)")

print("\n" + "="*80)
print("测试Django数据库连接")
print("="*80)

django_test = '''cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/var/www/eims')

try:
    import django
    django.setup()
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"✅ Django数据库连接成功: {result}")
except Exception as e:
    print(f"❌ Django数据库错误: {e}")
    import traceback
    traceback.print_exc()
PYEOF
'''

stdin, stdout, stderr = ssh.exec_command(django_test)
import time
time.sleep(3)
output = stdout.read().decode() + stderr.read().decode()
print(output if output.strip() else "(无输出)")

ssh.close()
