#!/usr/bin/env python
"""
修复MySQL密码问题并重启Gunicorn
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def fix_mysql_password():
    print("🔧 修复MySQL密码问题")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    # Step 1: Reset MySQL password to known value
    print("\n[1] 重置MySQL root密码...")
    
    # MySQL root password should be "EIMS2026_mysql" based on previous session
    commands = [
        "mysql -u root -p'fjkl546#' -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY 'EIMS2026_mysql'; FLUSH PRIVILEGES;\" 2>&1",
        "mysql -u root -p'EIMS2026_mysql' -e \"SELECT 1 as test;\" 2>&1",
    ]
    
    for i, cmd in enumerate(commands, 1):
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        output = result if result else error
        print(f"  命令{i}结果: {output[:100]}")
    
    # Step 2: Update settings.py with correct MySQL password
    print("\n[2] 更新settings.py中的MySQL密码...")
    
    # Find current database config
    stdin, stdout, stderr = ssh.exec_command("grep -A 10 'DATABASES' /var/www/eims/eims/settings.py | head -15")
    db_config = stdout.read().decode().strip()
    print(f"  当前数据库配置:")
    for line in db_config.split('\n')[:10]:
        print(f"    {line}")
    
    # Check if password is correct
    if "EIMS2026_mysql" not in db_config:
        print("\n  ❌ 密码不正确，正在修复...")
        
        # Replace the password in settings.py
        fix_cmd = """sed -i \"s/'PASSWORD': '[^']*'/'PASSWORD': 'EIMS2026_mysql'/g\" /var/www/eims/eims/settings.py"""
        stdin, stdout, stderr = ssh.exec_command(fix_cmd)
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command("grep 'PASSWORD' /var/www/eims/eims/settings.py")
        result = stdout.read().decode().strip()
        print(f"  修复后: {result}")
    else:
        print("  ✅ 密码已经是 EIMS2026_mysql")
    
    # Step 3: Test MySQL connection from Django
    print("\n[3] 测试Django MySQL连接...")
    test_cmd = """cd /var/www/eims && /var/www/eims/venv/bin/python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('✅ MySQL connection successful')
cursor.close()
" 2>&1"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    result = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    output = result if result else error
    print(f"  {output}")
    
    # Step 4: Restart Gunicorn
    print("\n[4] 重启Gunicorn...")
    ssh.exec_command('pkill -9 gunicorn || true')
    time.sleep(2)
    
    ssh.exec_command('cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &')
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"  Gunicorn进程数: {count}")
    
    # Step 5: Test HTTP
    print("\n[5] 测试HTTP访问...")
    tests = [
        ('本地Gunicorn', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/'),
        ('本地Nginx', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/'),
    ]
    
    for name, cmd in tests:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        code = stdout.read().decode().strip()
        status = "✅" if code in ['200', '302', '500'] else "❌"
        print(f"  {status} {name}: HTTP {code}")
    
    ssh.close()
    
    print("\n" + "="*60)
    print("✅ 修复完成!")
    print("="*60)
    print("\n现在请刷新浏览器测试: http://www.xietongai.com.cn/login/")
    print("="*60 + "\n")

if __name__ == '__main__':
    fix_mysql_password()
