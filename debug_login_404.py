import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("诊断登录页面 404 问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查 Django URL 配置
    print("\n[1] 检查主 URL 配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/urls.py 2>&1')
    urls_content = stdout.read().decode('utf-8')
    print("urls.py 内容:")
    print(urls_content[:1000])
    
    # 2. 检查是否有 login URL
    print("\n[2] 搜索 login URL 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -rn "login" /var/www/eims/urls.py /var/www/eims/*/urls.py /var/www/eims/eims_app/*/urls.py 2>/dev/null | head -20')
    login_urls = stdout.read().decode('utf-8')
    print("Login URL 配置:")
    print(login_urls)
    
    # 3. 检查所有 URL 配置
    print("\n[3] 查看所有 URL 配置...")
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "urls.py" -type f 2>/dev/null')
    url_files = stdout.read().decode('utf-8')
    print("URL 文件:")
    print(url_files)
    
    # 4. 检查 eims_app 的 URL 配置
    print("\n[4] 检查 eims_app/urls.py...")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/eims_app/urls.py 2>&1 | head -50')
    eims_urls = stdout.read().decode('utf-8')
    print(eims_urls)
    
    # 5. 测试不同的 URL 路径
    print("\n[5] 测试不同的 URL 路径...")
    
    test_urls = [
        '/',
        '/login/',
        '/login',
        '/accounts/login/',
        '/auth/login/',
        '/user/login/',
    ]
    
    for url in test_urls:
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8000{url}')
        status = stdout.read().decode('utf-8').strip()
        print(f"  {url:30s} -> HTTP {status}")
    
    # 6. 检查 Django URL 路由
    print("\n[6] 检查 Django URL 路由...")
    check_urls = r'''
import os
import sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.urls import get_resolver

resolver = get_resolver()
print("\n所有 URL 模式:")
for pattern in resolver.url_patterns:
    print(f"  {pattern}")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/check_urls.py << "URLEOF"\n{check_urls}\nURLEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/check_urls.py 2>&1')
    url_patterns = stdout.read().decode('utf-8')
    print(url_patterns)
    
    # 7. 检查主 urls.py 中的 include
    print("\n[7] 检查主 urls.py 的完整内容...")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/urls.py')
    full_urls = stdout.read().decode('utf-8')
    print(full_urls)
    
    # 8. 测试直接通过 Nginx 访问
    print("\n[8] 测试 Nginx 代理...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1/ | head -20')
    nginx_response = stdout.read().decode('utf-8')
    print("Nginx 响应（前20行）:")
    print(nginx_response)
    
    # 9. 检查 Nginx 错误日志
    print("\n[9] 检查 Nginx 错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/nginx_error.log 2>&1')
    nginx_errors = stdout.read().decode('utf-8')
    if nginx_errors.strip():
        print("Nginx 错误日志:")
        print(nginx_errors)
    else:
        print("Nginx 错误日志为空")
    
    # 10. 检查 Django 错误日志
    print("\n[10] 检查 Django/Gunicorn 错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    django_errors = stdout.read().decode('utf-8')
    if django_errors.strip():
        print("Django 错误日志:")
        print(django_errors[-1500:])
    else:
        print("Django 错误日志为空")
    
    print("\n" + "="*70)
    print("✅ 诊断完成")
    print("="*70)
    
    print("\n下一步建议:")
    print("1. 检查主 urls.py 是否正确 include 了 eims_app 的 URL")
    print("2. 确认登录视图的 URL 路径是否正确")
    print("3. 检查是否需要重启 Gunicorn")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
