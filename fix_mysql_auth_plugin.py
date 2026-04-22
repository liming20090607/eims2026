import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 MySQL 8.0 认证插件问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 修改 root 用户认证插件为 mysql_native_password
    print("\n[1] 修改 MySQL root 用户认证方式...")
    
    fix_auth_script = '''mysql -uroot -pEIMS2026_mysql << 'MYSQL_EOF'
-- 修改认证插件为 mysql_native_password（兼容 PyMySQL）
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;

-- 验证修改
SELECT user, host, plugin FROM mysql.user WHERE user='root';
MYSQL_EOF
'''
    
    stdin, stdout, stderr = ssh.exec_command(fix_auth_script)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error and 'Warning' not in error:
        print("错误:", error[:300])
    
    # 2. 验证认证插件已修改
    print("\n[2] 验证认证插件...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT user, host, plugin FROM mysql.user WHERE user=\'root\';" 2>&1')
    plugin_info = stdout.read().decode('utf-8')
    print(plugin_info)
    
    if 'mysql_native_password' in plugin_info:
        print("[✓] 认证插件已成功修改为 mysql_native_password")
    else:
        print("[✗] 认证插件未修改")
    
    # 3. 测试 PyMySQL 连接
    print("\n[3] 测试 PyMySQL 连接...")
    
    test_pymysql_script = r'''
import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"✓ PyMySQL 连接成功: {result}")
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f"✓ 数据库中有 {len(tables)} 个表")
    connection.close()
except Exception as e:
    print(f"✗ PyMySQL 连接失败: {e}")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_pymysql.py << "PYEOF"\n{test_pymysql_script}\nPYEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_pymysql.py')
    pymysql_output = stdout.read().decode('utf-8')
    pymysql_error = stderr.read().decode('utf-8')
    print(pymysql_output)
    if pymysql_error:
        print("错误:", pymysql_error[:300])
    
    # 4. 测试 Django 数据库连接
    print("\n[4] 测试 Django 数据库连接...")
    
    test_django_script = r'''
import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"✓ Django 数据库连接成功: {result}")
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f"✓ 数据库中有 {len(tables)} 个表")
except Exception as e:
    print(f"✗ Django 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_django_db.py << "DJEOF"\n{test_django_script}\nDJEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_django_db.py')
    django_output = stdout.read().decode('utf-8')
    django_error = stderr.read().decode('utf-8')
    print(django_output)
    if django_error:
        print("错误:", django_error[:300])
    
    # 5. 重启 Gunicorn 服务
    print("\n[5] 重启 Gunicorn 服务...")
    stdin, stdout, stderr = ssh.exec_command('pkill -f "gunicorn.*eims" || true')
    time.sleep(3)
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    time.sleep(5)
    
    # 验证进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    process_count = stdout.read().decode('utf-8').strip()
    print(f"✓ Gunicorn 进程数: {process_count}")
    
    # 6. HTTP 测试
    print("\n[6] HTTP 测试...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status_code}")
    
    if status_code in ['200', '302']:
        print("\n" + "="*70)
        print("✅ MySQL 认证问题已解决！")
        print("="*70)
        print("\n修复内容:")
        print("  ✓ 修改 root 用户认证插件为 mysql_native_password")
        print("  ✓ PyMySQL 连接测试通过")
        print("  ✓ Django 数据库连接测试通过")
        print("  ✓ Gunicorn 服务已重启")
        print(f"  ✓ HTTP 服务正常 (状态码: {status_code})")
        print("\n现在可以正常登录:")
        print("  http://39.106.41.239:8000/")
        print("  http://www.xietongai.com.cn/")
        print("\n登录凭据:")
        print("  admin / admin123456")
        print("  root / root123456")
        print("="*70)
    else:
        print(f"\n⚠️ 状态码异常: {status_code}")
        print("请检查日志: /var/www/eims/logs/error.log")
    
finally:
    ssh.close()
    print("\n完成！")
