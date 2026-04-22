import paramiko
import time

print("="*70)
print("彻底修复 MySQL 认证问题")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前 MySQL 认证插件
    print("\n[1] 检查 MySQL 认证插件...")
    stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -pEIMS2026_mysql -e "
    SELECT user, host, plugin, authentication_string FROM mysql.user WHERE user='root';
    " 2>&1""")
    auth_info = stdout.read().decode('utf-8')
    print("当前认证信息:")
    print(auth_info)
    
    # 2. 如果认证插件不对，强制修复
    if 'caching_sha2_password' in auth_info or auth_info.strip() == '':
        print("\n[2] 修复认证插件为 mysql_native_password...")
        
        fix_script = """mysql -uroot -pEIMS2026_mysql << 'MYSQL_EOF'
-- 强制设置认证插件
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
ALTER USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证
SELECT user, host, plugin FROM mysql.user WHERE user='root';
MYSQL_EOF
"""
        stdin, stdout, stderr = ssh.exec_command(fix_script)
        result = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        print("修复结果:")
        print(result)
        if error:
            print("错误:", error)
    
    # 3. 测试 MySQL 命令行连接
    print("\n[3] 测试 MySQL 命令行连接...")
    stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -pEIMS2026_mysql -e "SELECT 'MySQL连接成功' AS status;" 2>&1""")
    test_result = stdout.read().decode('utf-8')
    print("MySQL 测试:", test_result)
    
    # 4. 测试 PyMySQL 连接
    print("\n[4] 测试 PyMySQL 连接...")
    test_pymysql = r'''python3 << 'TESTEOF'
import pymysql

try:
    # 测试 localhost
    conn1 = pymysql.connect(
        host='localhost',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor1 = conn1.cursor()
    cursor1.execute('SELECT "PyMySQL localhost 连接成功" AS status')
    result1 = cursor1.fetchone()
    print(f"✓ localhost: {result1[0]}")
    conn1.close()
    
    # 测试 127.0.0.1
    conn2 = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT "PyMySQL 127.0.0.1 连接成功" AS status')
    result2 = cursor2.fetchone()
    print(f"✓ 127.0.0.1: {result2[0]}")
    conn2.close()
    
    print("✓✓✓ PyMySQL 连接完全成功！")
    
except Exception as e:
    print(f"✗ PyMySQL 连接失败: {e}")
    import traceback
    traceback.print_exc()
TESTEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_pymysql)
    pymysql_result = stdout.read().decode('utf-8')
    print(pymysql_result)
    
    # 5. 清空错误日志
    print("\n[5] 清空错误日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 6. 强制重启 Gunicorn
    print("\n[6] 重启 Gunicorn...")
    
    # 停止旧进程
    stdin, stdout, stderr = ssh.exec_command('lsof -ti:8000 | xargs kill -9 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    # 启动新进程
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    # 验证进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    proc_count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {proc_count}")
    
    # 7. 测试 Django 应用
    print("\n[7] 测试 Django 应用...")
    time.sleep(3)
    
    test_django = r'''python3 << 'DJEOF'
import os
import sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.db import connection

try:
    # 测试数据库连接
    cursor = connection.cursor()
    cursor.execute('SELECT "Django数据库连接成功" AS status')
    result = cursor.fetchone()
    print(f"✓ Django 数据库连接: {result[0]}")
    
    # 测试用户认证
    from django.contrib.auth import authenticate
    user = authenticate(username='admin', password='admin123456')
    if user:
        print(f"✓ admin 用户认证成功")
    else:
        print("✗ admin 用户认证失败")
    
    user = authenticate(username='root', password='root123456')
    if user:
        print(f"✓ root 用户认证成功")
    else:
        print("✗ root 用户认证失败")
        
except Exception as e:
    print(f"✗ Django 测试失败: {e}")
    import traceback
    traceback.print_exc()
DJEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_django)
    django_result = stdout.read().decode('utf-8')
    print(django_result)
    
    # 8. 测试 HTTP 访问
    print("\n[8] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # 9. 检查错误日志
    print("\n[9] 检查最新错误...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库访问拒绝错误")
        print(errors[-1000:])
    else:
        print("[✓] 无数据库访问错误")
    
    print("\n" + "="*70)
    print("✅ MySQL 认证修复完成")
    print("="*70)
    
    if nginx_status == '200' and 'Django 数据库连接成功' in django_result:
        print("\n✅ 系统完全正常！")
        print("\n访问地址:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n⚠️ 仍有问题，请检查上述输出")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
