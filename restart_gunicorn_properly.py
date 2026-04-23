import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("=" * 70)
print("完全重启 Gunicorn 服务")
print("=" * 70)

# 1. 停止所有 Gunicorn 进程
print("\n[1/5] 停止所有 Gunicorn 进程...")
stdin, stdout, stderr = ssh.exec_command("pkill -9 -f gunicorn || true")
time.sleep(3)

# 验证进程已停止
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"剩余 Gunicorn 进程: {count}")

# 2. 确认 .env 文件正确
print("\n[2/5] 确认 .env 文件内容...")
stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/.env")
env_content = stdout.read().decode()
print(env_content)

# 3. 使用 Python 直接启动 Gunicorn（确保读取 .env）
print("\n[3/5] 启动 Gunicorn...")

# 创建一个启动脚本
start_script = """
import os
import sys

# 读取 .env 文件
env_file = '/var/www/eims/.env'
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# 切换到项目目录
os.chdir('/var/www/eims')

# 启动 Gunicorn
from gunicorn.app.wsgiapp import run
sys.argv = ['gunicorn', '--bind', '127.0.0.1:8000', '--workers', '4', '--timeout', '300', '--daemon', 'wsgi:application']
run()
"""

# 写入启动脚本
stdin, stdout, stderr = ssh.exec_command(f"cat > /tmp/start_gunicorn.py <<'PYEOF'\n{start_script}PYEOF")
time.sleep(1)

# 执行启动脚本
stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && source venv/bin/activate && python /tmp/start_gunicorn.py")
time.sleep(5)

# 4. 验证进程
print("\n[4/5] 验证 Gunicorn 进程...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"Gunicorn 进程数: {count}")

# 5. 测试网站
print("\n[5/5] 测试网站访问...")
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"HTTP 状态码: {http_status}")

# 检查最新日志
print("\n检查最新日志（最后30行）...")
stdin, stdout, stderr = ssh.exec_command("tail -30 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || tail -30 /var/www/eims/gunicorn_error.log 2>/dev/null || echo 'No log found'")
log_output = stdout.read().decode()
print(log_output[-1500:] if len(log_output) > 1500 else log_output)

print("\n" + "=" * 70)
if http_status == '200' and 'Access denied' not in log_output[-500:]:
    print("✅ 成功！网站应该可以正常使用了")
else:
    print("⚠️  可能还有问题，请检查上方日志")
print("访问地址: http://www.xietongai.com.cn/login/")
print("=" * 70)

ssh.close()
