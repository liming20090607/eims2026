import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("重启 Gunicorn 并验证...")

# 停止 Gunicorn
ssh.exec_command("pkill -9 -f gunicorn || true")
time.sleep(3)

# 启动 Gunicorn
ssh.exec_command("/var/www/eims/start_gunicorn.sh")
time.sleep(5)

# 测试网站
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"HTTP 状态码: {http_status}")

# 检查错误
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("tail -10 /var/www/eims/logs/gunicorn_error.log | grep -i 'ConnectionDoesNotExist\\|root_admin' || echo 'No connection errors'")
errors = stdout.read().decode()
print(f"连接错误: {errors.strip()}")

if http_status == '200' and 'No connection errors' in errors:
    print("\n✅ 成功！")
else:
    print("\n⚠️  还有问题")
    
ssh.close()
