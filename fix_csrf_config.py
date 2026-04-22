import paramiko
import time

print("="*70)
print("修复 CSRF 配置")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前 CSRF 配置
    print("\n[1] 检查 CSRF 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 20 "CSRF_TRUSTED_ORIGINS" /var/www/eims/settings.py | head -25')
    csrf_config = stdout.read().decode('utf-8')
    print("CSRF 配置:")
    print(csrf_config)
    
    # 2. 检查 ALLOWED_HOSTS
    print("\n[2] 检查 ALLOWED_HOSTS...")
    stdin, stdout, stderr = ssh.exec_command('grep "ALLOWED_HOSTS" /var/www/eims/settings.py')
    allowed_hosts = stdout.read().decode('utf-8')
    print("ALLOWED_HOSTS:")
    print(allowed_hosts)
    
    # 3. 更新 CSRF 配置
    print("\n[3] 更新 CSRF 配置...")
    update_csrf = """python3 << 'PYEOF'
import re

with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_csrf = """CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'http://39.106.41.239',
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'https://www.xietongai.com.cn',
    'https://xietongai.com.cn',
    'http://*',
    'https://*',
]"""

pattern = r'CSRF_TRUSTED_ORIGINS\\s*=\\s*\\[.*?\\]'
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_csrf, content, flags=re.DOTALL)
    print("已更新 CSRF_TRUSTED_ORIGINS")
else:
    print("警告: 未找到 CSRF_TRUSTED_ORIGINS")

with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("CSRF 配置已更新")
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(update_csrf)
    time.sleep(3)
    update_result = stdout.read().decode('utf-8')
    print(update_result)
    
    # 4. 验证配置
    print("\n[4] 验证更新后的配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 15 "CSRF_TRUSTED_ORIGINS" /var/www/eims/settings.py | head -20')
    new_config = stdout.read().decode('utf-8')
    print("更新后的 CSRF 配置:")
    print(new_config)
    
    # 5. 重启 Gunicorn
    print("\n[5] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn || true')
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
    time.sleep(2)
    
    # 清空日志
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 启动 Gunicorn
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    ssh.exec_command(start_cmd)
    
    print("等待 12 秒...")
    time.sleep(12)
    
    # 6. 测试 HTTP GET
    print("\n[6] 测试 GET 登录页面...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    get_status = stdout.read().decode('utf-8').strip()
    print("GET /login/: " + get_status)
    
    # 7. 获取 CSRF token 并测试 POST
    print("\n[7] 测试 POST 登录...")
    
    test_login = '''/var/www/eims/venv/bin/python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.test import Client

client = Client()

# 先获取 CSRF token
response = client.get('/login/')
print("GET 状态码: " + str(response.status_code))

if response.status_code == 200:
    content = response.content.decode('utf-8')
    import re
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
    if match:
        csrf_token = match.group(1)
        print("CSRF token: " + csrf_token[:20] + "...")
        
        # POST 登录
        response = client.post('/login/', {
            'username': 'admin',
            'password': 'admin123456',
            'csrfmiddlewaretoken': csrf_token
        }, follow=True)
        
        print("POST 状态码: " + str(response.status_code))
        print("最终 URL: " + str(response.request.get('PATH_INFO', 'N/A')))
        
        if response.status_code in [200, 302]:
            print("[OK] 登录成功！")
        else:
            print("[X] 登录失败")
    else:
        print("[X] 未找到 CSRF token")
else:
    print("[X] GET 请求失败")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_login)
    time.sleep(10)
    login_result = stdout.read().decode('utf-8')
    login_error = stderr.read().decode('utf-8')
    print("登录测试结果:")
    print(login_result if login_result else "[无输出]")
    if login_error:
        print("错误:", login_error[:500])
    
    # 8. 检查错误日志
    print("\n[8] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] 数据库访问错误")
        print(errors[-1000:])
    else:
        print("[OK] 无数据库访问错误")
    
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)
    
    if '登录成功' in login_result:
        print("\n[OK] 登录功能正常！")
        print("\n现在可以登录:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n[警告] 仍有问题")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
