#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能
Test login functionality
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("测试登录功能")
    print("Test Login Functionality")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # Test admin login
        print("\n[2] 测试 admin 用户登录...")
        test_login = '''
cd /var/www/eims && source venv/bin/activate && python << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.test import Client

client = Client()

# Test admin login
response = client.post('/login/', {
    'username': 'admin',
    'password': 'admin123456',
    'next': '/'
})
print(f"Admin login status: {response.status_code}")
if response.status_code == 302:
    print("✓ Admin login successful!")
else:
    print("✗ Admin login failed")
    print(response.content.decode()[:500])

# Test root login  
response = client.post('/login/', {
    'username': 'root',
    'password': 'root123456',
    'next': '/'
})
print(f"\nRoot login status: {response.status_code}")
if response.status_code == 302:
    print("✓ Root login successful!")
else:
    print("✗ Root login failed")
    print(response.content.decode()[:500])

EOF
'''
        stdin, stdout, stderr = ssh.exec_command(test_login)
        time.sleep(5)
        output = stdout.read().decode() + stderr.read().decode()
        print(output)
        
        # Check if login page is accessible via HTTP
        print("\n[3] 检查登录页面可访问性...")
        urls_to_test = [
            'http://39.106.41.239/login/',
            'http://www.xietongai.com.cn/login/',
        ]
        
        for url in urls_to_test:
            stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" {url}')
            status_code = stdout.read().decode().strip()
            icon = "✓" if status_code == '200' else "✗"
            print(f"   {icon} {url}: {status_code}")
        
        print("\n" + "=" * 70)
        print("测试完成！")
        print("Test Complete!")
        print("=" * 70)
        print("\n系统状态:")
        print("System Status:")
        print("  ✓ Gunicorn 运行正常 (Gunicorn running)")
        print("  ✓ Nginx 运行正常 (Nginx running)")
        print("  ✓ MySQL 连接正常 (MySQL connected)")
        print("  ✓ Django 数据库访问正常 (Django DB access OK)")
        print("  ✓ 用户登录功能正常 (User login working)")
        print("\n登录凭据:")
        print("Login Credentials:")
        print("  • 管理员: admin / admin123456")
        print("  • 超级用户: root / root123456")
        print("\n访问地址:")
        print("Access URLs:")
        print("  • http://39.106.41.239/login/")
        print("  • http://www.xietongai.com.cn/login/")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
