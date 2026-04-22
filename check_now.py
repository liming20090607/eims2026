#!/usr/bin/env python
"""
快速检查系统当前状态
"""

import paramiko
import requests
from datetime import datetime

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def check_server_status():
    print(f"\n{'='*60}")
    print(f"系统状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**SSH_CONFIG, timeout=10)
        
        # 检查服务状态
        checks = {
            'MySQL': 'systemctl is-active mysqld',
            'Nginx进程': 'pgrep -c nginx',
            'Gunicorn进程': 'pgrep -c gunicorn',
            '端口80': 'ss -tlnp | grep ":80 " | wc -l',
            '端口8000': 'ss -tlnp | grep ":8000 " | wc -l',
        }
        
        print("【服务状态】")
        for name, cmd in checks.items():
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode().strip()
            status = "✅" if result and result != '0' and result != 'inactive' else "❌"
            print(f"  {status} {name}: {result}")
        
        # HTTP测试
        print("\n【HTTP测试】")
        
        tests = [
            ('本地Nginx', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/'),
            ('本地Gunicorn', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/'),
            ('服务器IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://39.106.41.239/login/'),
        ]
        
        for name, cmd in tests:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            code = stdout.read().decode().strip()
            status = "✅" if code in ['200', '302', '500'] else "❌"
            print(f"  {status} {name}: HTTP {code}")
        
        # 检查CSRF配置
        print("\n【CSRF配置】")
        stdin, stdout, stderr = ssh.exec_command('grep -A 6 "CSRF_TRUSTED_ORIGINS" /var/www/eims/eims/settings.py')
        csrf_config = stdout.read().decode().strip()
        if csrf_config:
            print("  ✅ CSRF配置存在")
            for line in csrf_config.split('\n')[:7]:
                print(f"    {line}")
        else:
            print("  ❌ CSRF配置缺失")
        
        # 检查自动纠错系统
        print("\n【自动纠错系统】")
        stdin, stdout, stderr = ssh.exec_command('ls -lh /usr/local/bin/auto_correction.sh')
        result = stdout.read().decode().strip()
        if result:
            print("  ✅ 脚本已部署")
            print(f"    {result.split()[-2]} {result.split()[-1]}")
        else:
            print("  ❌ 脚本未部署")
        
        # 检查cron
        stdin, stdout, stderr = ssh.exec_command('crontab -l | grep auto_correction')
        cron = stdout.read().decode().strip()
        if cron:
            print("  ✅ 已添加到cron")
        else:
            print("  ❌ 未添加到cron")
        
        # 最近的日志
        print("\n【最近纠错日志】")
        stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/auto_correction.log 2>/dev/null')
        logs = stdout.read().decode().strip()
        if logs:
            for line in logs.split('\n')[-5:]:
                print(f"  {line}")
        else:
            print("  (无日志)")
        
        # 检查Nginx错误日志
        print("\n【Nginx最近错误】")
        stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/nginx_error.log 2>/dev/null')
        errors = stdout.read().decode().strip()
        if errors:
            for line in errors.split('\n')[-3:]:
                if line.strip():
                    print(f"  ⚠️ {line.strip()[:100]}")
        else:
            print("  ✅ 无错误")
        
        ssh.close()
        
        print(f"\n{'='*60}")
        print("💡 建议:")
        print("  1. 如果HTTP返回502: Gunicorn可能崩溃，需要重启")
        print("  2. 如果HTTP返回500: Django应用错误，检查错误日志")
        print("  3. 如果外部访问失败: 需要在阿里云控制台开放80端口")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ 连接失败: {str(e)}\n")

if __name__ == '__main__':
    check_server_status()
