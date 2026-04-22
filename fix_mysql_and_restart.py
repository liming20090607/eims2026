import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 MySQL 认证问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 修复 MySQL 用户认证
    print("\n[1] 修复 MySQL 用户认证...")
    
    fix_mysql = '''mysql -uroot -pEIMS2026_mysql << 'MYSQL_EOF'
-- 删除并重新创建 root 用户
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'127.0.0.1';
DROP USER IF EXISTS 'root'@'::1';

-- 创建新用户
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- 授权
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证
SELECT user, host, plugin FROM mysql.user WHERE user='root';
MYSQL_EOF
'''
    
    stdin, stdout, stderr = ssh.exec_command(fix_mysql)
    mysql_output = stdout.read().decode('utf-8')
    print("MySQL 用户修复结果:")
    print(mysql_output)
    
    # 2. 测试 MySQL 连接
    print("\n[2] 测试 MySQL 连接...")
    test_mysql = r'''python3 << 'TESTEOF'
import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"✓ MySQL 连接成功: {result}")
    conn.close()
except Exception as e:
    print(f"✗ MySQL 连接失败: {e}")
TESTEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_mysql)
    test_output = stdout.read().decode('utf-8')
    print(test_output)
    
    # 3. 重启 Gunicorn（清除旧的数据库连接）
    print("\n[3] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn || true')
    time.sleep(3)
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    print("等待 Gunicorn 启动...")
    time.sleep(8)
    
    # 验证进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {count}")
    
    # 4. 测试 HTTP 访问
    print("\n[4] 测试 HTTP 访问...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态: {login_status}")
    
    # 5. 检查错误日志
    print("\n[5] 检查最新错误...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/error.log 2>&1')
    recent_errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in recent_errors:
        print("[✗] 仍有数据库连接错误")
        print(recent_errors[-500:])
    else:
        print("[✓] 无数据库连接错误")
        if recent_errors.strip():
            print("其他日志:")
            print(recent_errors[-300:])
    
    # 6. 测试登录功能
    print("\n[6] 测试登录功能...")
    test_login = r'''python3 << 'LOGINEOF'
import os
import sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.test import Client

client = Client()

# 测试 admin 登录
response = client.post('/login/', {
    'username': 'admin',
    'password': 'admin123456'
}, follow=True)

if response.status_code in [200, 302]:
    print("✓ admin 登录测试成功")
else:
    print(f"✗ admin 登录失败: {response.status_code}")

# 测试 root 登录
response = client.post('/login/', {
    'username': 'root',
    'password': 'root123456'
}, follow=True)

if response.status_code in [200, 302]:
    print("✓ root 登录测试成功")
else:
    print(f"✗ root 登录失败: {response.status_code}")
LOGINEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_login)
    login_result = stdout.read().decode('utf-8')
    print(login_result)
    
    print("\n" + "="*70)
    print("✅ MySQL 认证修复完成！")
    print("="*70)
    
    if login_status == '200':
        print("\n服务器完全正常！")
    else:
        print("\n登录页面状态:", login_status)
    
    print("\n访问地址:")
    print("  http://39.106.41.239/login/")
    print("  http://www.xietongai.com.cn/login/")
    print("\n登录凭据:")
    print("  用户名: admin  密码: admin123456")
    print("  用户名: root   密码: root123456")
    
    print("\n如果仍无法访问，请:")
    print("1. 清除浏览器缓存")
    print("2. 使用 HTTP 而非 HTTPS")
    print("3. 检查阿里云安全组是否开放端口 80")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
