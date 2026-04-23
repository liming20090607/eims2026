import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("=" * 70)
print("诊断环境变量加载问题")
print("=" * 70)

# 1. 测试 dotenv 加载
print("\n[测试 1] 检查 dotenv 是否能正确加载 .env")
test_script = """
import os
import sys
sys.path.insert(0, '/var/www/eims')
from dotenv import load_dotenv

env_path = '/var/www/eims/.env'
print(f".env 文件存在: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path) as f:
        print(f".env 内容:")
        print(f.read())

load_dotenv(env_path)
print(f"DB_PASSWORD from env: {os.getenv('DB_PASSWORD')}")
"""

stdin, stdout, stderr = ssh.exec_command(f"cd /var/www/eims && source venv/bin/activate && python3 <<'PYEOF'\n{test_script}PYEOF")
output = stdout.read().decode()
error = stderr.read().decode()
print(output)
if error:
    print("错误:", error)

# 2. 检查 settings.py 是否能正确加载
print("\n[测试 2] 检查 Django settings 加载")
stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && source venv/bin/activate && python -c 'import django; django.setup(); from django.conf import settings; print(\"DB_PASSWORD:\", settings.DATABASES[\"default\"][\"PASSWORD\"])' 2>&1")
output = stdout.read().decode()
error = stderr.read().decode()
print(output)
if error and 'Traceback' in error:
    print("错误:", error[-500:])

# 3. 检查当前 Gunicorn 进程的环境变量
print("\n[测试 3] 检查 Gunicorn 进程的环境变量")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | head -1 | awk '{print $2}' | xargs -I {} cat /proc/{}/environ 2>/dev/null | tr '\\0' '\\n' | grep DB_")
output = stdout.read().decode()
print(f"Gunicorn 环境变量:\n{output}" if output else "无法读取 Gunicorn 环境变量")

print("\n" + "=" * 70)
ssh.close()
