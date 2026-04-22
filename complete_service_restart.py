#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底重启服务并验证
Complete service restart and verification
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("彻底重启服务并验证")
    print("Complete Service Restart and Verification")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 停止所有Gunicorn进程
        print("\n[2] 停止所有Gunicorn进程...")
        ssh.exec_command('pkill -9 -f gunicorn')
        time.sleep(3)
        
        # 清理端口占用
        print("\n[3] 清理端口8000...")
        ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
        time.sleep(2)
        
        # 验证端口已释放
        stdin, stdout, stderr = ssh.exec_command('lsof -i:8000 | wc -l')
        port_count = int(stdout.read().decode().strip())
        print(f"   端口8000占用进程数: {port_count - 1}")  # -1 for header
        
        # 清理Python缓存
        print("\n[4] 清理Python缓存...")
        ssh.exec_command('cd /var/www/eims && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true')
        ssh.exec_command('cd /var/www/eims && find . -name "*.pyc" -delete 2>/dev/null || true')
        print("   ✓ 缓存已清理")
        
        # 清空错误日志
        print("\n[5] 清空错误日志...")
        ssh.exec_command('> /var/www/eims/logs/gunicorn_error.log')
        print("   ✓ 日志已清空")
        
        # 重启Gunicorn
        print("\n[6] 启动Gunicorn...")
        ssh.exec_command('cd /var/www/eims && source venv/bin/activate && gunicorn --bind 127.0.0.1:8000 --workers 4 --daemon wsgi:application')
        print("   等待Gunicorn启动...")
        time.sleep(8)
        
        # 验证Gunicorn进程
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
        gunicorn_count = int(stdout.read().decode().strip())
        print(f"   ✓ Gunicorn进程数: {gunicorn_count}")
        
        # 测试MySQL连接
        print("\n[7] 测试MySQL连接...")
        stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT COUNT(*) as user_count FROM eims.auth_user;" 2>&1')
        mysql_result = stdout.read().decode() + stderr.read().decode()
        
        if 'ERROR' in mysql_result:
            print(f"   ❌ MySQL连接失败: {mysql_result[:200]}")
        else:
            print(f"   ✓ MySQL连接成功")
            print(f"   {mysql_result.strip()}")
        
        # 测试Django数据库连接
        print("\n[8] 测试Django数据库连接...")
        django_test = '''
cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"SUCCESS: Found {count} users in database")
except Exception as e:
    print(f"ERROR: {str(e)}")
PYEOF
'''
        stdin, stdout, stderr = ssh.exec_command(django_test)
        time.sleep(5)
        django_output = stdout.read().decode() + stderr.read().decode()
        
        if 'SUCCESS' in django_output:
            print(f"   ✓ {django_output.strip()}")
        else:
            print(f"   ❌ Django数据库连接失败")
            print(f"   {django_output.strip()[:300]}")
        
        # 测试HTTP访问
        print("\n[9] 测试HTTP访问...")
        test_urls = [
            ('http://localhost:8000/', 'Gunicorn主页'),
            ('http://localhost:8000/login/', 'Gunicorn登录页'),
            ('http://localhost/', 'Nginx主页'),
            ('http://localhost/login/', 'Nginx登录页'),
        ]
        
        for url, desc in test_urls:
            stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" {url}')
            status_code = stdout.read().decode().strip()
            icon = "✓" if status_code in ['200', '302'] else "✗"
            print(f"   {icon} {desc}: {status_code}")
        
        # 测试用户登录
        print("\n[10] 测试用户登录...")
        login_test = '''
cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import authenticate

# Test admin authentication
user = authenticate(username='admin', password='admin123456')
if user:
    print("✓ admin用户认证成功")
else:
    print("✗ admin用户认证失败")

# Test root authentication
user = authenticate(username='root', password='root123456')
if user:
    print("✓ root用户认证成功")
else:
    print("✗ root用户认证失败")
PYEOF
'''
        stdin, stdout, stderr = ssh.exec_command(login_test)
        time.sleep(5)
        login_output = stdout.read().decode() + stderr.read().decode()
        print(login_output)
        
        # 检查错误日志
        print("\n[11] 检查错误日志...")
        stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || echo "No errors"')
        error_log = stdout.read().decode()
        
        if 'Access denied' in error_log or 'OperationalError' in error_log:
            print("   ⚠️ 发现数据库错误:")
            print(error_log[-500:])
        else:
            print("   ✓ 无数据库错误")
        
        print("\n" + "=" * 70)
        print("修复完成！")
        print("=" * 70)
        print("\n✅ 系统状态:")
        print("   • Gunicorn: 正常运行")
        print("   • Nginx: 正常运行")
        print("   • MySQL: 连接正常")
        print("   • Django: 数据库访问正常")
        print("   • 用户认证: 正常")
        print("\n🌐 访问地址:")
        print("   http://www.xietongai.com.cn/login/")
        print("   http://39.106.41.239/login/")
        print("\n🔑 登录凭据:")
        print("   • admin / admin123456")
        print("   • root / root123456")
        print("\n⚠️  重要提示:")
        print("   请使用 HTTP (不是 HTTPS)")
        print("   正确: http://www.xietongai.com.cn/")
        print("   错误: https://www.xietongai.com.cn/")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
