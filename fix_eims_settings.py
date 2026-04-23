import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

print("=" * 70)
print("修复服务器上的 eims/settings.py 并重启服务")
print("=" * 70)

# 检查当前 eims/settings.py 中的 load_dotenv 调用
print("\n[1/5] 检查当前 eims/settings.py 的 load_dotenv 配置...")
stdin, stdout, stderr = ssh.exec_command("grep -n 'load_dotenv' /var/www/eims/eims/settings.py")
current = stdout.read().decode()
print(f"当前配置:\n{current}")

# 备份当前文件
print("\n[2/5] 备份当前 settings.py...")
ssh.exec_command("cp /var/www/eims/eims/settings.py /var/www/eims/eims/settings.py.bak.$(date +%Y%m%d_%H%M%S)")

# 修复 load_dotenv 调用
print("\n[3/5] 修复 load_dotenv 调用...")
fix_script = """
import re

with open('/var/www/eims/eims/settings.py', 'r') as f:
    content = f.read()

# 替换 load_dotenv() 为 load_dotenv('/var/www/eims/.env')
content = re.sub(r'load_dotenv\\(\\)', "load_dotenv('/var/www/eims/.env')", content)

with open('/var/www/eims/eims/settings.py', 'w') as f:
    f.write(content)

print("✅ 已修复 eims/settings.py")
"""

stdin, stdout, stderr = ssh.exec_command(f"python3 <<'PYEOF'\n{fix_script}PYEOF")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("错误:", err)

# 验证修复
print("\n[4/5] 验证修复...")
stdin, stdout, stderr = ssh.exec_command("grep -n 'load_dotenv' /var/www/eims/eims/settings.py")
print(f"修复后配置:\n{stdout.read().decode()}")

# 重启 Gunicorn
print("\n[5/5] 重启 Gunicorn 服务...")
ssh.exec_command("pkill -9 -f gunicorn || true")

import time
time.sleep(3)

# 使用启动脚本
stdin, stdout, stderr = ssh.exec_command("/var/www/eims/start_gunicorn.sh")
time.sleep(5)

# 测试
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w 'HTTP: %{http_code}\\n' http://127.0.0.1:8000/login/")
http_status = stdout.read().decode().strip()
print(f"\nHTTP 状态码: {http_status}")

# 检查最新错误
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("tail -20 /var/www/eims/logs/gunicorn_error.log | grep -i 'access denied\\|1045' || echo 'No password errors in recent logs'")
errors = stdout.read().decode()
print(f"密码错误检查: {errors}")

print("\n" + "=" * 70)
if http_status == '200' and 'No password errors' in errors:
    print("✅ 修复成功！")
    print("\n请在浏览器中访问并测试:")
    print("http://www.xietongai.com.cn/login/")
else:
    print("⚠️  可能还有问题，请检查:")
    print("ssh root@39.106.41.239")
    print("tail -f /var/www/eims/logs/gunicorn_error.log")
print("=" * 70)

ssh.close()
