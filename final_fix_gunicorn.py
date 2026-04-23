import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("=" * 70)
print("最终修复：确保 Django 使用正确的 .env 配置")
print("=" * 70)

# 1. 停止所有 Gunicorn
print("\n[1/6] 停止所有 Gunicorn 进程...")
ssh.exec_command("pkill -9 -f gunicorn || true")
time.sleep(3)

# 2. 确认 .env 文件
print("\n[2/6] 确认 .env 文件...")
stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/.env")
print(stdout.read().decode())

# 3. 创建启动脚本（确保加载 .env）
print("\n[3/6] 创建 Gunicorn 启动脚本...")
start_script = r"""#!/bin/bash
cd /var/www/eims
source venv/bin/activate

# 导出 .env 中的所有变量
set -a
source .env
set +a

# 设置 Django settings module
export DJANGO_SETTINGS_MODULE=settings

# 启动 Gunicorn
exec gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    wsgi:application
"""

stdin, stdout, stderr = ssh.exec_command(f"cat > /var/www/eims/start_gunicorn.sh <<'BASHEOF'\n{start_script}BASHEOF")
ssh.exec_command("chmod +x /var/www/eims/start_gunicorn.sh")
time.sleep(1)

# 4. 启动服务
print("\n[4/6] 启动 Gunicorn...")
stdin, stdout, stderr = ssh.exec_command("/var/www/eims/start_gunicorn.sh")
time.sleep(5)

# 5. 验证
print("\n[5/6] 验证服务...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"Gunicorn 进程数: {count}")

stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"HTTP 状态码: {http_status}")

# 6. 检查最新日志
print("\n[6/6] 检查最新日志...")
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("tail -50 /var/www/eims/logs/gunicorn_error.log 2>/dev/null | grep -A 5 -B 5 'OperationalError\\|Access denied\\|Database' || echo 'No database errors in recent logs'")
recent_logs = stdout.read().decode()
print(recent_logs[-1000:] if len(recent_logs) > 1000 else recent_logs)

print("\n" + "=" * 70)
if http_status == '200' and 'Access denied' not in recent_logs:
    print("✅ 成功！网站应该可以正常使用了")
    print("\n请在浏览器中访问并测试登录:")
    print("http://www.xietongai.com.cn/login/")
else:
    print("⚠️  可能还有问题")
    print("\n最新错误日志:")
    print(recent_logs[-500:])
print("=" * 70)

ssh.close()
