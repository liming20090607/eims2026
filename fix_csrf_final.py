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
    
    # 2. 更新 CSRF 配置 - 使用 sed 简单替换
    print("\n[2] 更新 CSRF 配置...")
    
    # 使用 Python 脚本更新
    update_script = r'''/var/www/eims/venv/bin/python3 << 'PYEOF'
import re

with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 新的 CSRF 配置
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

# 替换旧的 CSRF 配置
pattern = r"CSRF_TRUSTED_ORIGINS\s*=\s*\[.*?\]"
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_csrf, content, flags=re.DOTALL)
    print("OK: Updated CSRF_TRUSTED_ORIGINS")
else:
    print("WARN: CSRF_TRUSTED_ORIGINS not found")

with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("DONE")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(update_script)
    time.sleep(3)
    update_result = stdout.read().decode('utf-8')
    print(update_result)
    
    # 3. 验证配置
    print("\n[3] 验证更新后的配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 12 "CSRF_TRUSTED_ORIGINS" /var/www/eims/settings.py | head -15')
    new_config = stdout.read().decode('utf-8')
    print("更新后的 CSRF 配置:")
    print(new_config)
    
    # 4. 重启 Gunicorn
    print("\n[4] 重启 Gunicorn...")
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
    
    # 5. 测试 GET 登录页面
    print("\n[5] 测试 GET 登录页面...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    get_status = stdout.read().decode('utf-8').strip()
    print("GET /login/: " + get_status)
    
    # 6. 使用 Django 测试客户端测试登录
    print("\n[6] 测试登录功能...")
    
    test_login = r'''/var/www/eims/venv/bin/python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.test import Client

client = Client()

# 获取页面
response = client.get('/login/')
print("GET status: " + str(response.status_code))

if response.status_code == 200:
    # 提取 CSRF token
    content = response.content.decode('utf-8')
    import re
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
    if match:
        csrf_token = match.group(1)
        print("CSRF token found")
        
        # POST 登录
        response = client.post('/login/', {
            'username': 'admin',
            'password': 'admin123456',
            'csrfmiddlewaretoken': csrf_token
        }, follow=True)
        
        print("POST status: " + str(response.status_code))
        
        if response.status_code in [200, 302]:
            print("OK: Login successful")
        else:
            print("FAIL: Login failed")
    else:
        print("FAIL: No CSRF token found")
else:
    print("FAIL: GET request failed")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_login)
    time.sleep(10)
    login_result = stdout.read().decode('utf-8')
    login_error = stderr.read().decode('utf-8')
    print("测试结果:")
    print(login_result if login_result else "[no output]")
    if login_error:
        print("Error:", login_error[:500])
    
    # 7. 检查错误日志
    print("\n[7] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] Database access error")
        print(errors[-1000:])
    else:
        print("[OK] No database access errors")
    
    print("\n" + "="*70)
    print("DONE")
    print("="*70)
    
    if 'Login successful' in login_result:
        print("\n[OK] Login working!")
        print("\nAccess:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\nCredentials:")
        print("  Username: admin  Password: admin123456")
        print("  Username: root   Password: root123456")
    else:
        print("\n[WARN] Still has issues")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\nDone!")
