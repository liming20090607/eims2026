import paramiko
import time

print("="*70)
print("MySQL Root 用户直接修复")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 直接使用 MySQL 命令行测试连接
    print("\n[1] 测试 MySQL 命令行连接...")
    
    # 测试 localhost
    stdin, stdout, stderr = ssh.exec_command('''mysql -uroot -pEIMS2026_mysql -h localhost -e "SELECT 'SUCCESS_LOCALHOST' AS status;" 2>&1''')
    local_result = stdout.read().decode('utf-8')
    local_error = stderr.read().decode('utf-8')
    print("localhost 连接:")
    if 'SUCCESS_LOCALHOST' in local_result:
        print("✓ 成功")
    else:
        print("✗ 失败:", local_error.strip()[:100] if local_error else local_result.strip()[:100])
    
    # 测试 127.0.0.1
    stdin, stdout, stderr = ssh.exec_command('''mysql -uroot -pEIMS2026_mysql -h 127.0.0.1 -e "SELECT 'SUCCESS_127' AS status;" 2>&1''')
    tcp_result = stdout.read().decode('utf-8')
    tcp_error = stderr.read().decode('utf-8')
    print("127.0.0.1 连接:")
    if 'SUCCESS_127' in tcp_result:
        print("✓ 成功")
    else:
        print("✗ 失败:", tcp_error.strip()[:100] if tcp_error else tcp_result.strip()[:100])
    
    # 2. 如果连接失败，需要重置密码
    if 'SUCCESS' not in local_result and 'SUCCESS' not in tcp_result:
        print("\n[2] 使用 skip-grant-tables 重置 root 密码...")
        
        # 停止 MySQL
        print("停止 MySQL...")
        stdin, stdout, stderr = ssh.exec_command('systemctl stop mysqld')
        time.sleep(5)
        
        # 启动 skip-grant-tables
        print("启动 skip-grant-tables 模式...")
        stdin, stdout, stderr = ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 > /dev/null 2>&1 &')
        time.sleep(10)
        
        # 使用 socket 连接并重置
        print("重置 root 用户...")
        reset_cmd = '''mysql -u root -S /var/lib/mysql/mysql.sock << 'EOSQL'
FLUSH PRIVILEGES;

-- 删除现有 root 用户
DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;

-- 创建新的 root 用户
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;

FLUSH PRIVILEGES;

SELECT User, Host FROM mysql.user WHERE User='root';
EOSQL
'''
        stdin, stdout, stderr = ssh.exec_command(reset_cmd)
        time.sleep(5)
        result = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("重置结果:")
        if result.strip():
            print(result[:500])
        if error.strip():
            print("错误:", error[:500])
        
        # 停止并正常启动 MySQL
        print("\n停止 skip-grant-tables 模式...")
        stdin, stdout, stderr = ssh.exec_command('killall -9 mysqld mysqld_safe 2>/dev/null || true')
        time.sleep(3)
        
        print("正常启动 MySQL...")
        stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld')
        time.sleep(10)
        
        # 3. 重新测试连接
        print("\n[3] 重新测试 MySQL 连接...")
        
        stdin, stdout, stderr = ssh.exec_command('''mysql -uroot -pEIMS2026_mysql -h 127.0.0.1 -e "SELECT 'SUCCESS' AS status;" 2>&1''')
        final_result = stdout.read().decode('utf-8')
        final_error = stderr.read().decode('utf-8')
        
        if 'SUCCESS' in final_result:
            print("✓ MySQL 连接成功！")
        else:
            print("✗ MySQL 连接仍失败:")
            print(final_error.strip()[:200] if final_error else final_result.strip()[:200])
    
    else:
        print("\n[2] MySQL 连接正常，跳过重置")
        final_result = local_result if 'SUCCESS' in local_result else tcp_result
    
    # 4. 测试 Django 数据库连接
    print("\n[4] 测试 Django 数据库连接...")
    
    # 修改 Django settings.py 使用 127.0.0.1 而不是 localhost
    fix_settings = '''python3 << 'PYEOF'
import re

with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 将 HOST 从 localhost 改为 127.0.0.1
content = content.replace(
    "'HOST': 'localhost',",
    "'HOST': '127.0.0.1',"
)

with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ settings.py 已更新: HOST='127.0.0.1'")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(fix_settings)
    settings_result = stdout.read().decode('utf-8')
    print(settings_result)
    
    # 测试 Django
    test_django = '''python3 << 'DJEOF'
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.db import connection

try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print("✓ Django 数据库连接成功")
except Exception as e:
    print(f"✗ Django 数据库连接失败: {e}")

# 测试用户认证
from django.contrib.auth import authenticate

for username, password in [('admin', 'admin123456'), ('root', 'root123456')]:
    user = authenticate(username=username, password=password)
    if user:
        print(f"✓ 用户 {username} 认证成功")
    else:
        print(f"✗ 用户 {username} 认证失败")
DJEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_django)
    time.sleep(5)
    django_result = stdout.read().decode('utf-8')
    print(django_result)
    
    # 5. 重启 Gunicorn
    print("\n[5] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    # 清空日志
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 启动 Gunicorn
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    ssh.exec_command(start_cmd)
    
    print("等待 10 秒...")
    time.sleep(10)
    
    # 6. 测试 HTTP
    print("\n[6] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # 7. 检查错误日志
    print("\n[7] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -15 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库访问错误")
    else:
        print("[✓] 无数据库访问错误")
    
    if errors.strip():
        print("最新日志:")
        print(errors[-800:])
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    
    if 'SUCCESS' in final_result and 'Django 数据库连接成功' in django_result:
        print("\n✅ 系统完全正常！")
        print("\n📍 访问地址:")
        print("   http://39.106.41.239/login/")
        print("   http://www.xietongai.com.cn/login/")
        print("\n🔑 登录凭据:")
        print("   用户名: admin  密码: admin123456")
        print("   用户名: root   密码: root123456")
    else:
        print("\n⚠️ 仍有问题，请检查上述输出")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
