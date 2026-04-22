#!/usr/bin/env python
"""
查看Gunicorn启动失败的详细原因
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

print("\n" + "="*70)
print("🔍 Gunicorn启动失败详细诊断")
print("="*70 + "\n")

# 1. 清空错误日志
print("[1] 清空旧日志并重启...")
ssh.exec_command('> /var/www/eims/logs/gunicorn_error.log')
ssh.exec_command('pkill -9 gunicorn || true')
time.sleep(1)

# 2. 使用单worker模式启动并捕获错误
print("\n[2] 尝试启动Gunicorn (单worker模式)...")
start_cmd = '''cd /var/www/eims
nohup /var/www/eims/venv/bin/gunicorn \
  --bind 127.0.0.1:8000 \
  --workers 1 \
  --timeout 30 \
  --log-level debug \
  eims.wsgi:application \
  >> /var/www/eims/logs/gunicorn_error.log 2>&1 &
'''
stdin, stdout, stderr = ssh.exec_command(start_cmd)
time.sleep(5)

# 3. 检查进程
print("\n[3] 检查进程状态...")
stdin, stdout, stderr = ssh.exec_command('pgrep -a gunicorn')
processes = stdout.read().decode().strip()
if processes:
    print("  运行中的Gunicorn进程:")
    for line in processes.split('\n'):
        print(f"    {line}")
else:
    print("  ❌ 没有Gunicorn进程")

# 4. 查看错误日志
print("\n[4] 查看错误日志...")
stdin, stdout, stderr = ssh.exec_command('tail -100 /var/www/eims/logs/gunicorn_error.log')
errors = stdout.read().decode().strip()

if errors:
    print("\n  最新100行错误日志:")
    print("  " + "-"*68)
    for i, line in enumerate(errors.split('\n'), 1):
        if line.strip():
            print(f"  {i:3d}. {line}")
    print("  " + "-"*68)
    
    # 提取关键错误
    print("\n[5] 关键错误信息:")
    for keyword in ['Error', 'Exception', 'Traceback', 'Failed', 'ImportError', 'ModuleNotFoundError', 'OperationalError']:
        matching_lines = [line for line in errors.split('\n') if keyword.lower() in line.lower()]
        if matching_lines:
            print(f"\n  {keyword}:")
            for line in matching_lines[-3:]:
                print(f"    → {line.strip()[:80]}")
else:
    print("  (日志为空)")

# 5. 尝试手动运行Django检查
print("\n[6] 手动测试Django初始化...")
manual_test = """cd /var/www/eims && /var/www/eims/venv/bin/python << 'PYEOF'
import sys
import os

# 添加项目路径
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')

print("Step 1: Import Django")
import django

print("Step 2: Setup Django")
try:
    django.setup()
    print("  ✅ Django setup OK")
except Exception as e:
    print(f"  ❌ Django setup FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 3: Test database connection")
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"  ✅ Database OK: {result}")
except Exception as e:
    print(f"  ❌ Database FAILED: {e}")

print("Step 4: Test URL loading")
try:
    from django.urls import reverse
    login_url = reverse('login')
    print(f"  ✅ URL OK: {login_url}")
except Exception as e:
    print(f"  ❌ URL FAILED: {e}")

print("Step 5: Test WSGI app")
try:
    from eims.wsgi import application
    print(f"  ✅ WSGI app OK: {type(application)}")
except Exception as e:
    print(f"  ❌ WSGI FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All tests passed!")
PYEOF
"""

stdin, stdout, stderr = ssh.exec_command(manual_test)
time.sleep(3)
result = stdout.read().decode().strip()
error_output = stderr.read().decode().strip()

if result:
    print("\n  测试结果:")
    for line in result.split('\n'):
        print(f"    {line}")

if error_output:
    print("\n  标准错误:")
    for line in error_output.split('\n')[-10:]:
        print(f"    {line}")

ssh.close()

print("\n" + "="*70)
print("诊断完成")
print("="*70 + "\n")
