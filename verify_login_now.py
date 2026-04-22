#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证系统登录功能
"""
import paramiko
import time

SSH_HOST = '39.106.41.239'
SSH_USER = 'root'
SSH_PASS = 'EIMS2026_root'

def ssh_exec(ssh, command, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_status, output, error

print("=" * 70)
print("🔍 系统登录功能验证")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ 已连接服务器\n")
    
    # 检查服务状态
    print("[1] 服务状态:")
    _, mysql_status, _ = ssh_exec(ssh, 'systemctl is-active mysqld')
    _, gunicorn_count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    _, nginx_count, _ = ssh_exec(ssh, 'pgrep -c nginx || echo "0"')
    
    print(f"  MySQL:    {mysql_status}")
    print(f"  Gunicorn: {gunicorn_count} workers")
    print(f"  Nginx:    {nginx_count} processes\n")
    
    # 如果Gunicorn没有运行，启动它
    if int(gunicorn_count) == 0:
        print("[2] 启动Gunicorn...")
        
        # 先确认wsgi.py存在
        _, wsgi_check, _ = ssh_exec(ssh, 'ls -lh /var/www/eims/eims/wsgi.py 2>&1')
        if 'No such file' in wsgi_check:
            print("  ⚠️ wsgi.py不存在，正在创建...")
            wsgi_content = '''"""
WSGI config for EIMS2026 project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
application = get_wsgi_application()
'''
            ssh_exec(ssh, f'cat > /var/www/eims/eims/wsgi.py << EOF\n{wsgi_content}\nEOF')
            print("  ✅ wsgi.py 已创建")
        
        # 启动Gunicorn
        ssh_exec(ssh, 'pkill -9 gunicorn || true')
        time.sleep(2)
        
        start_cmd = '''cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn \
            --bind 127.0.0.1:8000 \
            --workers 5 \
            --timeout 120 \
            --chdir /var/www/eims \
            eims.wsgi:application \
            --access-logfile /var/www/eims/logs/gunicorn_access.log \
            --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'''
        
        ssh_exec(ssh, start_cmd)
        time.sleep(5)
        
        _, new_count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
        print(f"  ✅ Gunicorn workers: {new_count}\n")
    else:
        print("[2] Gunicorn已在运行\n")
    
    # 测试HTTP访问
    print("[3] HTTP测试:")
    _, nginx_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
    _, gunicorn_code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/')
    
    print(f"  Nginx (80):      HTTP {nginx_code}")
    print(f"  Gunicorn (8000): HTTP {gunicorn_code}\n")
    
    # 检查错误日志
    if nginx_code not in ['200', '302']:
        print("[4] 错误日志:")
        _, errors, _ = ssh_exec(ssh, 'tail -20 /var/www/eims/logs/gunicorn_error.log')
        print(f"{errors}\n")
    else:
        # 验证页面内容
        print("[4] 页面内容验证:")
        _, title, _ = ssh_exec(ssh, 'curl -s http://127.0.0.1:80/login/ | grep -o "<title>.*</title>"')
        print(f"  {title}\n")
        
        # 检查settings.py密码配置
        print("[5] MySQL密码配置:")
        _, pwd_check, _ = ssh_exec(ssh, 'grep "PASSWORD.*EIMS2026_mysql" /var/www/eims/eims/settings.py | wc -l')
        print(f"  找到 {pwd_check} 个正确密码配置\n")
    
    print("=" * 70)
    if nginx_code in ['200', '302']:
        print("✅ 系统运行正常！")
        print("\n🌐 可以访问:")
        print("   http://www.xietongai.com.cn/login/")
        print("   http://39.106.41.239/login/")
    else:
        print("❌ 系统仍有问题")
        print("\n可能的原因:")
        print("  1. MySQL密码错误")
        print("  2. settings.py配置问题")
        print("  3. Gunicorn启动失败")
        print("\n请检查上面的错误日志")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
