#!/usr/bin/env python
"""
检查当前MySQL密码配置并修复
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def check_and_fix():
    print("🔍 检查MySQL密码配置")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    # 1. 查看settings.py中的数据库密码
    print("\n[1] 当前settings.py中的数据库配置:")
    stdin, stdout, stderr = ssh.exec_command("grep -A 8 \"'default':\" /var/www/eims/eims/settings.py | grep -E \"'ENGINE'|'NAME'|'USER'|'PASSWORD'|'HOST'|'PORT'\"")
    config = stdout.read().decode().strip()
    print(config)
    
    # 2. 测试MySQL连接
    print("\n[2] 测试MySQL连接...")
    
    # Try different passwords
    passwords_to_try = ['EIMS2026_mysql', 'fjkl546#', 'root', '']
    working_password = None
    
    for pwd in passwords_to_try:
        cmd = f"mysql -u root -p'{pwd}' -e \"SELECT 1 as test;\" 2>&1"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode().strip()
        if '1' in result:
            working_password = pwd
            print(f"  ✅ 密码 '{pwd}' 可以正常工作")
            break
        else:
            print(f"  ❌ 密码 '{pwd}' 无效")
    
    if not working_password:
        # Try to reset MySQL password
        print("\n[3] MySQL需要重置密码...")
        
        # Try to stop MySQL and start with skip-grant-tables
        print("  尝试通过skip-grant-tables重置密码...")
        ssh.exec_command('systemctl stop mysqld')
        time.sleep(2)
        
        # Start MySQL without password check
        stdin, stdout, stderr = ssh.exec_command('mysqld_safe --skip-grant-tables &')
        time.sleep(5)
        
        # Reset password
        reset_cmd = """mysql -u root << 'EOF'
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
EOF"""
        stdin, stdout, stderr = ssh.exec_command(reset_cmd)
        time.sleep(2)
        
        # Restart MySQL normally
        ssh.exec_command('systemctl stop mysqld')
        time.sleep(2)
        ssh.exec_command('systemctl start mysqld')
        time.sleep(3)
        
        # Test
        stdin, stdout, stderr = ssh.exec_command("mysql -u root -p'EIMS2026_mysql' -e \"SELECT 1 as test;\" 2>&1")
        result = stdout.read().decode().strip()
        if '1' in result:
            working_password = 'EIMS2026_mysql'
            print("  ✅ MySQL密码已重置为 'EIMS2026_mysql'")
        else:
            print("  ❌ 密码重置失败")
    
    if working_password:
        # Update settings.py
        print("\n[4] 更新settings.py中的密码...")
        
        # Use Python to safely update the password
        update_cmd = f"""python3 << 'EOF'
import re

settings_file = '/var/www/eims/eims/settings.py'
with open(settings_file, 'r') as f:
    content = f.read()

# Replace PASSWORD value in DATABASES
pattern = r"('PASSWORD':\\s*')[^']*(')"
replacement = r"\\1{password}\\2"
new_content = re.sub(pattern, replacement.format(password='{pwd}'), content)

with open(settings_file, 'w') as f:
    f.write(new_content)

print('✅ Password updated in settings.py')
EOF"""
        
        # Simpler approach
        simple_update = f"""sed -i "s/'PASSWORD': '.*'/'PASSWORD': '{working_password}'/g" /var/www/eims/eims/settings.py"""
        stdin, stdout, stderr = ssh.exec_command(simple_update)
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command("grep 'PASSWORD' /var/www/eims/eims/settings.py")
        print(f"  更新后: {stdout.read().decode().strip()}")
    
    # 3. 重启Gunicorn
    print("\n[5] 重启Gunicorn...")
    ssh.exec_command('pkill -9 gunicorn || true')
    time.sleep(2)
    ssh.exec_command('cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &')
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"  Gunicorn进程数: {count}")
    
    # 4. 测试
    print("\n[6] 测试访问...")
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
    print("请刷新浏览器测试: http://www.xietongai.com.cn/login/")
    print("="*60)

if __name__ == '__main__':
    check_and_fix()
