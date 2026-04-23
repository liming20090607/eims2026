import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("=" * 70)
print("修复云服务器配置并重启服务")
print("=" * 70)

# 1. 创建 .env 文件
print("\n[1/4] 创建 .env 配置文件...")
env_commands = [
    "echo 'DB_NAME=eims' > /var/www/eims/.env",
    "echo 'DB_USER=root' >> /var/www/eims/.env",
    "echo 'DB_PASSWORD=mysql2026!' >> /var/www/eims/.env",
    "echo 'DB_HOST=localhost' >> /var/www/eims/.env",
    "echo 'DB_PORT=3306' >> /var/www/eims/.env"
]

for cmd in env_commands:
    ssh.exec_command(cmd)
    time.sleep(0.5)

# 验证 .env 文件
stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/.env")
print(stdout.read().decode())

# 2. 验证 MySQL 密码
print("\n[2/4] 验证 MySQL 密码...")
stdin, stdout, stderr = ssh.exec_command('mysql -u root -pmysql2026! -e "SELECT 1" 2>&1')
output = stdout.read().decode()
error = stderr.read().decode()

if 'Access denied' in error:
    print("❌ MySQL 密码验证失败！")
    print("Error:", error)
    ssh.close()
    exit(1)
else:
    print("✅ MySQL 密码验证成功")

# 3. 启动 Gunicorn
print("\n[3/4] 启动 Gunicorn 服务...")
ssh.exec_command("pkill -9 -f gunicorn || true")
time.sleep(2)

start_cmd = """cd /var/www/eims && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    wsgi:application"""

stdin, stdout, stderr = ssh.exec_command(start_cmd)
time.sleep(4)

# 4. 验证服务
print("\n[4/4] 验证服务状态...")

# 检查 Gunicorn 进程
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
process_count = stdout.read().decode().strip()
print(f"Gunicorn 进程数: {process_count}")

# 测试网站
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"HTTP 状态码: {http_status}")

# 检查错误日志
print("\n检查最近的错误日志...")
stdin, stdout, stderr = ssh.exec_command("tail -20 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || echo 'No error log found'")
print(stdout.read().decode())

print("\n" + "=" * 70)
if http_status == '200':
    print("✅ 修复完成！网站现在应该可以正常访问了")
    print("请访问: http://www.xietongai.com.cn/login/")
else:
    print("⚠️  网站可能还有问题，请检查日志")
print("=" * 70)

ssh.close()
