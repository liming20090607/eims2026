import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("修复 eims/settings.py 中的 load_dotenv() 调用...")

# 读取当前 settings.py
stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/eims/settings.py")
content = stdout.read().decode()

# 替换 load_dotenv() 为 load_dotenv('/var/www/eims/.env')
new_content = content.replace(
    'load_dotenv()',
    "load_dotenv('/var/www/eims/.env')"
)

# 写回文件
stdin, stdout, stderr = ssh.exec_command(f"cat > /var/www/eims/eims/settings.py <<'PYEOF'\n{new_content}PYEOF")

print("✅ 已更新 eims/settings.py")

# 验证修改
stdin, stdout, stderr = ssh.exec_command("grep -A 1 'load_dotenv' /var/www/eims/eims/settings.py | head -5")
print("验证修改:")
print(stdout.read().decode())

# 重启 Gunicorn
print("\n重启 Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn || true")

import time
time.sleep(2)

ssh.exec_command("cd /var/www/eims && /var/www/eims/start_gunicorn.sh")
time.sleep(5)

# 测试
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"\nHTTP 状态码: {http_status}")

# 检查错误
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("tail -30 /var/www/eims/logs/gunicorn_error.log | grep -i 'access denied\\|1045' || echo 'No password errors!'")
errors = stdout.read().decode()
print(f"密码错误: {errors}")

print("\n" + "=" * 70)
if http_status == '200' and 'No password errors' in errors:
    print("✅ 成功！")
else:
    print("⚠️  请检查日志")
print("访问: http://www.xietongai.com.cn/login/")
print("=" * 70)

ssh.close()
