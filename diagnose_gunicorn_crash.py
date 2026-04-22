#!/usr/bin/env python
"""
检查Gunicorn为什么一直崩溃
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
print("🔍 Gunicorn崩溃原因诊断")
print("="*70 + "\n")

# 1. 检查错误日志
print("[1] Gunicorn错误日志:")
stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
errors = stdout.read().decode().strip()
if errors:
    for line in errors.split('\n')[-20:]:
        print(f"  {line}")
else:
    print("  (无日志)")

# 2. 尝试手动启动Gunicorn并查看错误
print("\n[2] 手动启动测试:")
test_cmd = """cd /var/www/eims && /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 1 eims.wsgi:application 2>&1 | head -30 &
sleep 5
kill %1 2>/dev/null
"""
stdin, stdout, stderr = ssh.exec_command(test_cmd)
time.sleep(6)
output = stdout.read().decode().strip()
if output:
    for line in output.split('\n')[-15:]:
        print(f"  {line}")
else:
    print("  (无输出)")

# 3. 检查Python环境
print("\n[3] Python环境检查:")
checks = [
    ('Python版本', '/var/www/eims/venv/bin/python --version'),
    ('Django是否安装', '/var/www/eims/venv/bin/python -c "import django; print(django.VERSION)" 2>&1'),
    ('MySQL驱动', '/var/www/eims/venv/bin/python -c "import pymysql; print(pymysql.__version__)" 2>&1'),
    ('settings.py是否存在', 'test -f /var/www/eims/eims/settings.py && echo "YES" || echo "NO"'),
    ('settings.py大小', 'wc -c /var/www/eims/eims/settings.py'),
    ('wsgi.py是否存在', 'test -f /var/www/eims/wsgi.py && echo "YES" || echo "NO"'),
]

for name, cmd in checks:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    output = result if result else error
    print(f"  {name}: {output}")

# 4. 尝试导入Django
print("\n[4] Django导入测试:")
test_django = """cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import sys
print('Python path:', sys.path[:3])
import django
print('Django version:', django.VERSION)
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
print('Settings module set')
try:
    django.setup()
    print('✅ Django setup successful')
except Exception as e:
    print(f'❌ Django setup failed: {e}')
" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(test_django)
result = stdout.read().decode().strip()
for line in result.split('\n')[-10:]:
    print(f"  {line}")

# 5. 检查端口占用
print("\n[5] 端口8000占用情况:")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep :8000')
port_check = stdout.read().decode().strip()
if port_check:
    print(f"  ⚠️ 端口8000被占用:")
    print(f"  {port_check}")
else:
    print("  ✅ 端口8000空闲")

ssh.close()

print("\n" + "="*70)
print("📋 下一步建议:")
print("="*70)
print("\n如果settings.py有问题，需要重新上传")
print("如果Django导入失败，需要检查依赖")
print("="*70 + "\n")
