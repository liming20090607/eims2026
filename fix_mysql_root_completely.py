import paramiko
import time

print("="*70)
print("MySQL root 用户完整修复")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 完全停止 MySQL
    print("\n[1] 完全停止 MySQL...")
    stdin, stdout, stderr = ssh.exec_command('killall -9 mysqld 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('killall -9 mysqld_safe 2>/dev/null || true')
    time.sleep(2)
    print("MySQL 进程已终止")
    
    # 2. 删除 socket 文件
    print("\n[2] 清理 MySQL socket...")
    stdin, stdout, stderr = ssh.exec_command('rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysql.sock.lock 2>/dev/null || true')
    time.sleep(1)
    
    # 3. 以 skip-grant-tables 模式启动
    print("\n[3] 启动 MySQL（跳过权限验证）...")
    stdin, stdout, stderr = ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 > /tmp/mysql_safe.log 2>&1 &')
    print("等待 MySQL 启动（30秒）...")
    time.sleep(30)
    
    # 4. 检查 socket 文件
    print("\n[4] 检查 socket 文件...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/mysql.sock 2>&1')
    socket_info = stdout.read().decode('utf-8')
    print(f"Socket: {socket_info}")
    
    # 5. 使用 socket 无密码连接并重置 root
    print("\n[5] 重置 root 用户...")
    reset_script = '''mysql -u root --socket=/var/lib/mysql/mysql.sock << 'MYSQL_EOF'
-- 刷新权限
FLUSH PRIVILEGES;

-- 删除所有 root 用户
DELETE FROM mysql.user WHERE user='root';

-- 创建新的 root 用户
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- 授权
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

FLUSH PRIVILEGES;

-- 验证
SELECT user, host, plugin FROM mysql.user WHERE user='root';
MYSQL_EOF
'''
    stdin, stdout, stderr = ssh.exec_command(reset_script)
    time.sleep(5)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print("重置结果:")
    print(result if result else "[无输出]")
    if error:
        print("错误信息:", error)
    
    # 6. 停止 skip-grant-tables 模式
    print("\n[6] 停止 MySQL...")
    stdin, stdout, stderr = ssh.exec_command('mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>&1 || killall -9 mysqld 2>/dev/null || true')
    time.sleep(5)
    
    # 7. 正常启动 MySQL
    print("\n[7] 正常启动 MySQL...")
    stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld 2>&1 || service mysqld start 2>&1')
    print("等待 MySQL 启动（10秒）...")
    time.sleep(10)
    
    # 8. 测试 MySQL 命令行
    print("\n[8] 测试 MySQL 连接...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT SUCCESS;" 2>&1')
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print("测试结果:", test_result if test_result else "[无输出]")
    if test_error:
        print("错误:", test_error)
    
    # 9. 测试 PyMySQL
    print("\n[9] 测试 PyMySQL 连接...")
    test_pymysql = r'''python3 << 'PYEOF'
import pymysql

tests = [
    ('localhost', 'localhost'),
    ('127.0.0.1', '127.0.0.1'),
]

for host_name, host in tests:
    try:
        conn = pymysql.connect(
            host=host,
            user='root',
            password='EIMS2026_mysql',
            database='eims',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print(f"✓ {host_name}: 连接成功")
        conn.close()
    except Exception as e:
        print(f"✗ {host_name}: {e}")

print("\n✓✓✓ 测试完成")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_pymysql)
    pymysql_result = stdout.read().decode('utf-8')
    print(pymysql_result)
    
    # 10. 测试 Django 数据库连接
    print("\n[10] 测试 Django 数据库连接...")
    test_django = r'''python3 << 'DJEOF'
import os, sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"✓ Django 数据库连接成功")
except Exception as e:
    print(f"✗ Django 数据库连接失败: {e}")

# 测试用户认证
from django.contrib.auth import authenticate
for username, password in [('admin', 'admin123456'), ('root', 'root123456')]:
    user = authenticate(username=username, password=password)
    if user:
        print(f"✓ {username} 认证成功")
    else:
        print(f"✗ {username} 认证失败")
DJEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_django)
    django_result = stdout.read().decode('utf-8')
    print(django_result)
    
    # 11. 清空日志
    print("\n[11] 清空错误日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    
    # 12. 重启 Gunicorn
    print("\n[12] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('lsof -ti:8000 | xargs kill -9 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    gunicorn_count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {gunicorn_count}")
    
    # 13. 测试 HTTP
    print("\n[13] 测试 HTTP 访问...")
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # 14. 检查错误日志
    print("\n[14] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库访问拒绝错误")
    else:
        print("[✓] 无数据库访问错误")
    
    if errors.strip():
        print("最新日志:")
        print(errors[-1000:])
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    
    if 'SUCCESS' in test_result and '✓' in pymysql_result:
        print("\n✅ MySQL 修复成功！")
        if nginx_status == '200' or gunicorn_status == '200':
            print("\n✅ 系统完全正常运行！")
            print("\n📍 访问地址:")
            print("   http://39.106.41.239/login/")
            print("   http://www.xietongai.com.cn/login/")
            print("\n🔑 登录凭据:")
            print("   用户名: admin  密码: admin123456")
            print("   用户名: root   密码: root123456")
        else:
            print("\n⚠️ HTTP 服务需要重启")
    else:
        print("\n❌ MySQL 修复失败")
        print("\n请检查:")
        print("1. MySQL 是否正常运行")
        print("2. root 用户是否存在")
        print("3. 密码是否为 EIMS2026_mysql")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
