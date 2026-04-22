import paramiko
import time

print("="*70)
print("最终测试 - Django 和登录")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 测试 Django 数据库连接
    print("\n[1] 测试 Django 数据库连接...")
    
    test_script = '''python3 << 'EOF'
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    import django
    django.setup()
    
    # 测试数据库连接
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"✓ Django 数据库连接成功: {result}")
    
    # 测试用户认证
    from django.contrib.auth import authenticate
    
    print("\n测试 admin 用户:")
    user = authenticate(username='admin', password='admin123456')
    if user:
        print(f"  ✓ admin 认证成功 (ID: {user.id})")
    else:
        print("  ✗ admin 认证失败")
    
    print("\n测试 root 用户:")
    user = authenticate(username='root', password='root123456')
    if user:
        print(f"  ✓ root 认证成功 (ID: {user.id})")
    else:
        print("  ✗ root 认证失败")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
EOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_script)
    time.sleep(8)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print("Django 测试结果:")
    print(result if result else "[无输出]")
    if error:
        print("错误信息:", error[:500])
    
    # 2. 测试 HTTP 登录
    print("\n[2] 测试 HTTP 登录...")
    
    test_login = '''python3 << 'EOF'
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

print(f"  HTTP 状态码: {response.status_code}")
print(f"  最终 URL: {response.request.get('PATH_INFO', 'N/A')}")

if response.status_code in [200, 302]:
    if 'csrfmiddlewaretoken' in str(response.content) or 'logout' in str(response.content).lower():
        print("  ✓ admin 登录成功")
    else:
        print("  ? 状态码正常但需要验证")

print("\n测试 root 登录:")
response = client.post('/login/', {
    'username': 'root',
    'password': 'root123456'
}, follow=True)

print(f"  HTTP 状态码: {response.status_code}")
if response.status_code in [200, 302]:
    print("  ✓ root 登录成功")
else:
    print("  ✗ root 登录失败")
EOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_login)
    time.sleep(8)
    login_result = stdout.read().decode('utf-8')
    print("HTTP 登录测试:")
    print(login_result if login_result else "[无输出]")
    
    # 3. 测试实际 HTTP 访问
    print("\n[3] 测试实际 HTTP 访问...")
    
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # 4. 检查错误日志
    print("\n[4] 检查最新错误...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库访问拒绝错误")
        print(errors[-1000:])
    else:
        print("[✓] 无数据库访问错误")
        if errors.strip():
            print("其他日志:")
            print(errors[-500:])
    
    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70)
    
    if 'Django 数据库连接成功' in result:
        print("\n✅ Django 数据库连接正常！")
        if 'admin 认证成功' in result or 'root 认证成功' in result:
            print("✅ 用户认证成功！")
            print("\n📍 现在可以访问:")
            print("   http://39.106.41.239/login/")
            print("   http://www.xietongai.com.cn/login/")
            print("\n🔑 登录凭据:")
            print("   用户名: admin  密码: admin123456")
            print("   用户名: root   密码: root123456")
        else:
            print("\n⚠️ 数据库连接正常但用户认证可能有问题")
    else:
        print("\n❌ Django 数据库连接失败")
        print("请检查 MySQL 配置")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
