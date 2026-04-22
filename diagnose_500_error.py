import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("=" * 80)
print("🔍 诊断HTTP 500错误")
print("=" * 80)

# 检查Gunicorn错误日志
print("\n【1】Gunicorn错误日志（最近20行）:")
stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn.log 2>/dev/null || echo "日志文件不存在"')
log_output = stdout.read().decode()
if log_output.strip():
    print(log_output)
else:
    print("   (无错误日志)")

# 检查Django应用日志
print("\n【2】Django应用错误:")
django_check = '''cd /var/www/eims && source venv/bin/activate && python << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"✅ 数据库连接正常，用户数: {count}")
except Exception as e:
    print(f"❌ 数据库错误: {str(e)}")
EOF
'''
stdin, stdout, stderr = ssh.exec_command(django_check)
import time
time.sleep(3)
django_output = stdout.read().decode() + stderr.read().decode()
print(django_output if django_output.strip() else "   (无输出)")

# 测试直接访问Gunicorn
print("\n【3】直接访问Gunicorn (端口8000):")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}\\nTime: %{time_total}s" http://127.0.0.1:8000/login/')
result = stdout.read().decode().strip()
print(f"   {result}")

# 通过Nginx访问
print("\n【4】通过Nginx访问 (端口80):")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}\\nTime: %{time_total}s" http://127.0.0.1/login/')
result = stdout.read().decode().strip()
print(f"   {result}")

# 检查Nginx配置
print("\n【5】Nginx配置检查:")
stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -t 2>&1')
nginx_test = stdout.read().decode() + stderr.read().decode()
print(f"   {nginx_test}")

# 检查Nginx错误日志
print("\n【6】Nginx错误日志（最近10行）:")
stdin, stdout, stderr = ssh.exec_command('tail -10 /usr/local/nginx/logs/error.log 2>/dev/null | grep -i error || echo "无错误"')
nginx_errors = stdout.read().decode()
print(f"   {nginx_errors}")

print("\n" + "=" * 80)
print("💡 建议操作")
print("=" * 80)
print("\n如果看到数据库错误，执行:")
print("   python e:\\EIMS2026\\manual_fix_now.py")
print("\n如果只是临时问题，重启Gunicorn:")
print("   ssh root@39.106.41.239")
print("   pkill -9 -f gunicorn")
print("   cd /var/www/eims && source venv/bin/activate")
print("   nohup gunicorn --bind 127.0.0.1:8000 --workers 4 wsgi:application > logs/gunicorn.log 2>&1 &")

print("\n" + "=" * 80)

ssh.close()
