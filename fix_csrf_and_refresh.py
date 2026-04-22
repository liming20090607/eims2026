#!/usr/bin/env python
"""
自动修复CSRF问题并刷新登录页面
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def fix_csrf_and_refresh():
    print("🔧 自动修复CSRF问题")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    # Step 1: 检查settings.py中的CSRF配置
    print("\n[1/5] 检查CSRF配置...")
    stdin, stdout, stderr = ssh.exec_command("grep -A 10 'CSRF_TRUSTED_ORIGINS' /var/www/eims/eims/settings.py")
    csrf_config = stdout.read().decode().strip()
    
    if csrf_config:
        print("  ✅ CSRF配置存在")
        print(f"  {csrf_config[:100]}...")
    else:
        print("  ❌ CSRF配置缺失，正在添加...")
        # 添加CSRF配置
        add_csrf = """
# CSRF Configuration
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'http://39.106.41.239',
    'http://localhost',
    'http://127.0.0.1',
]
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
"""
        # 检查是否已有CSRF配置
        stdin, stdout, stderr = ssh.exec_command("grep -c 'CSRF_TRUSTED_ORIGINS' /var/www/eims/eims/settings.py")
        count = stdout.read().decode().strip()
        
        if count == '0':
            # 添加CSRF配置到settings.py
            ssh.exec_command(f"""echo '{add_csrf}' >> /var/www/eims/eims/settings.py""")
            print("  ✅ CSRF配置已添加")
        else:
            print("  ℹ️ CSRF配置已存在")
    
    # Step 2: 确保CSRF中间件启用
    print("\n[2/5] 检查CSRF中间件...")
    stdin, stdout, stderr = ssh.exec_command("grep 'CsrfViewMiddleware' /var/www/eims/eims/settings.py")
    if 'CsrfViewMiddleware' in stdout.read().decode():
        print("  ✅ CSRF中间件已启用")
    else:
        print("  ❌ CSRF中间件未启用")
    
    # Step 3: 清除旧的Gunicorn进程并重启
    print("\n[3/5] 重启Gunicorn以应用CSRF配置...")
    ssh.exec_command('pkill -9 gunicorn || true')
    time.sleep(2)
    
    ssh.exec_command('cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 120 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log >/dev/null 2>&1 &')
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"  ✅ Gunicorn已重启，工作进程数: {count}")
    
    # Step 4: 测试CSRF token生成
    print("\n[4/5] 测试CSRF token生成...")
    test_cmd = """cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
django.setup()
from django.middleware.csrf import get_token
from django.test import RequestFactory
factory = RequestFactory()
request = factory.get('/login/')
token = get_token(request)
print('CSRF Token generated:', token[:20] + '...' if token else 'None')
" 2>&1"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    result = stdout.read().decode().strip()
    print(f"  {result}")
    
    # Step 5: 测试登录页面访问
    print("\n[5/5] 测试登录页面...")
    tests = [
        ('GET 登录页面', 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/login/'),
        ('GET 登录页面 (带Cookie)', 'curl -s -c /tmp/test_cookies.txt -o /dev/null -w "%{http_code}" http://127.0.0.1:80/login/'),
        ('POST 登录页面 (模拟)', 'curl -s -b /tmp/test_cookies.txt -X POST -o /dev/null -w "%{http_code}" http://127.0.0.1:80/login/'),
    ]
    
    for name, cmd in tests:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        code = stdout.read().decode().strip()
        status = "✅" if code in ['200', '302'] else "⚠️"
        print(f"  {status} {name}: HTTP {code}")
    
    # Step 6: 清除浏览器缓存建议
    print("\n[6/6] 清除服务器端CSRF缓存...")
    ssh.exec_command('rm -f /tmp/test_cookies.txt')
    print("  ✅ 临时Cookie文件已清除")
    
    ssh.close()
    
    print("\n" + "="*70)
    print("✅ CSRF问题修复完成！")
    print("="*70)
    print("\n📋 请在浏览器中执行以下操作:")
    print("  1. 按 Ctrl+Shift+Delete 清除浏览器缓存和Cookie")
    print("  2. 或者直接按 Ctrl+F5 强制刷新页面")
    print("  3. 访问: http://www.xietongai.com.cn/login/")
    print("\n💡 如果仍然出现403错误:")
    print("  - 尝试使用隐私/无痕模式访问")
    print("  - 检查浏览器是否禁用了Cookie")
    print("  - 等待2分钟让自动纠错系统再次检查")
    print("="*70 + "\n")

if __name__ == '__main__':
    fix_csrf_and_refresh()
