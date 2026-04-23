import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("=" * 70)
print("最终修复部署")
print("=" * 70)

# 1. 确认 settings.py 已正确部署
print("\n[1/6] 确认 settings.py 已更新...")
stdin, stdout, stderr = ssh.exec_command("grep -A 3 'DB_PASSWORD' /var/www/eims/eims/settings.py | head -5")
print(stdout.read().decode())

# 2. 停止所有 Gunicorn
print("\n[2/6] 停止 Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn || true")
time.sleep(3)

# 3. 确认进程已停止
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"剩余进程数: {count}")

# 4. 启动 Gunicorn
print("\n[3/6] 启动 Gunicorn...")
ssh.exec_command("/var/www/eims/start_gunicorn.sh")
time.sleep(5)

# 5. 验证进程
stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
count = stdout.read().decode().strip()
print(f"\n[4/6] Gunicorn 进程数: {count}")

# 6. 测试 HTTP
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"[5/6] HTTP 状态码: {http_status}")

# 7. 检查错误日志
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("tail -20 /var/www/eims/logs/gunicorn_error.log")
logs = stdout.read().decode()
print(f"\n[6/6] 最新日志（最后20行）:")
print(logs[-800:] if len(logs) > 800 else logs)

print("\n" + "=" * 70)
if http_status == '200':
    print("✅ 部署成功！网站应该可以正常使用了")
    print("\n请在浏览器中测试:")
    print("http://www.xietongai.com.cn/login/")
else:
    print("⚠️  HTTP 状态异常，请检查日志")
print("=" * 70)

ssh.close()
