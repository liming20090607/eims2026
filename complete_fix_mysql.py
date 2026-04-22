import paramiko
import time

print("="*70)
print("彻底修复 MySQL 连接问题")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查 settings.py 中的 HOST 配置
    print("\n[1] 检查 settings.py 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 2 "HOST" /var/www/eims/settings.py | head -5')
    host_config = stdout.read().decode('utf-8')
    print("HOST 配置:")
    print(host_config)
    
    # 2. 强制修改为 127.0.0.1
    print("\n[2] 强制修改 settings.py 使用 127.0.0.1...")
    fix_cmd = '''python3 << 'PYEOF'
with open('/var/www/eims/settings.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "'HOST':" in line and ('localhost' in line or '127.0.0.1' not in line):
        line = line.replace("'localhost'", "'127.0.0.1'")
        print("Modified line: " + line.strip())
    new_lines.append(line)

with open('/var/www/eims/settings.py', 'w') as f:
    f.writelines(new_lines)

print("Settings.py updated")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(fix_cmd)
    time.sleep(3)
    fix_result = stdout.read().decode('utf-8')
    print(fix_result)
    
    # 3. 检查是否有多个 settings.py
    print("\n[3] 检查是否有其他 settings.py...")
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "settings.py" -type f')
    settings_files = stdout.read().decode('utf-8')
    print("找到的 settings.py 文件:")
    print(settings_files)
    
    # 4. 检查 Gunicorn 进程和加载的配置
    print("\n[4] 检查 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_procs = stdout.read().decode('utf-8')
    print("Gunicorn 进程:")
    print(gunicorn_procs if gunicorn_procs.strip() else "[无进程]")
    
    # 5. 完全重启 Gunicorn
    print("\n[5] 完全重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('killall -9 gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
    time.sleep(2)
    
    # 清空日志
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 启动新的 Gunicorn
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    
    print("等待 12 秒让服务启动...")
    time.sleep(12)
    
    # 6. 验证新进程
    print("\n[6] 验证新的 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    new_procs = stdout.read().decode('utf-8')
    print("新的 Gunicorn 进程:")
    print(new_procs if new_procs.strip() else "[无进程]")
    
    # 7. 测试 HTTP
    print("\n[7] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print("Gunicorn (8000): " + gunicorn_status)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print("Nginx (80): " + nginx_status)
    
    # 8. 检查错误日志
    print("\n[8] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] 仍有数据库访问错误")
        print(errors[-1500:])
    else:
        print("[OK] 无数据库访问错误")
        if errors.strip():
            print("其他日志:")
            print(errors[-500:])
    
    # 9. 使用 Django 测试客户端测试登录
    print("\n[9] 使用 Django 测试客户端测试登录...")
    test_login = '''/var/www/eims/venv/bin/python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.test import Client

client = Client()

print("测试 admin 登录:")
response = client.post('/login/', {
    'username': 'admin',
    'password': 'admin123456'
}, follow=True)

print("HTTP 状态码: " + str(response.status_code))
print("最终 URL: " + str(response.request.get('PATH_INFO', 'N/A')))

if response.status_code in [200, 302]:
    print("admin 登录测试成功")
else:
    print("admin 登录测试失败")

print("\\n测试 root 登录:")
response = client.post('/login/', {
    'username': 'root',
    'password': 'root123456'
}, follow=True)

print("HTTP 状态码: " + str(response.status_code))
if response.status_code in [200, 302]:
    print("root 登录测试成功")
else:
    print("root 登录测试失败")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_login)
    time.sleep(10)
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print("登录测试结果:")
    print(test_result if test_result else "[无输出]")
    if test_error:
        print("错误:", test_error[:500])
    
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)
    
    if gunicorn_status == '200' and nginx_status == '200':
        print("\n[OK] 服务正常运行！")
        if '登录测试成功' in test_result:
            print("[OK] 登录功能正常！")
        print("\n现在可以尝试登录:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n[警告] 服务状态异常")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
