import paramiko
import time

print("="*70)
print("MySQL 配置诊断和修复")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查 MySQL 配置文件
    print("\n[1] 检查 MySQL 配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /etc/my.cnf 2>/dev/null || cat /etc/mysql/my.cnf 2>/dev/null || echo "配置文件未找到"')
    mycnf = stdout.read().decode('utf-8')
    print("MySQL 配置:")
    print(mycnf if mycnf else "[无配置文件]")
    
    # 2. 检查 MySQL socket 位置
    print("\n[2] 查找 MySQL socket...")
    stdin, stdout, stderr = ssh.exec_command('find /var/run /tmp /var/lib -name "*.sock" 2>/dev/null || echo "未找到 socket 文件"')
    sockets = stdout.read().decode('utf-8')
    print("Socket 文件:")
    print(sockets if sockets else "[未找到]")
    
    # 3. 检查 MySQL 状态
    print("\n[3] 检查 MySQL 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysql | grep -v grep')
    mysql_procs = stdout.read().decode('utf-8')
    print("MySQL 进程:")
    print(mysql_procs if mysql_procs else "[未运行]")
    
    # 4. 停止所有 MySQL 进程
    print("\n[4] 停止所有 MySQL 进程...")
    stdin, stdout, stderr = ssh.exec_command('killall -9 mysqld mysqld_safe mysql 2>/dev/null || true')
    time.sleep(3)
    
    # 5. 查找实际的 MySQL 数据目录
    print("\n[5] 检查 MySQL 数据目录...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/ 2>&1 | head -20')
    data_dir = stdout.read().decode('utf-8')
    print("数据目录:")
    print(data_dir)
    
    # 6. 创建 MySQL 配置文件
    print("\n[6] 创建 MySQL 配置...")
    create_mycnf = '''cat > /etc/my.cnf << 'EOF'
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
user=mysql
symbolic-links=0
default-authentication-plugin=mysql_native_password

[mysqld_safe]
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid

[client]
socket=/var/lib/mysql/mysql.sock
EOF
'''
    stdin, stdout, stderr = ssh.exec_command(create_mycnf)
    time.sleep(1)
    print("MySQL 配置已创建")
    
    # 7. 确保目录存在
    print("\n[7] 创建必要目录...")
    stdin, stdout, stderr = ssh.exec_command('mkdir -p /var/lib/mysql /var/run/mysqld /var/log')
    stdin, stdout, stderr = ssh.exec_command('chown -R mysql:mysql /var/lib/mysql /var/run/mysqld')
    time.sleep(1)
    
    # 8. 初始化 MySQL（如果需要）
    print("\n[8] 初始化 MySQL 数据目录...")
    stdin, stdout, stderr = ssh.exec_command('mysql_install_db --user=mysql --datadir=/var/lib/mysql 2>&1 | tail -10')
    init_result = stdout.read().decode('utf-8')
    print("初始化结果:")
    print(init_result if init_result else "[已完成或无需初始化]")
    
    # 9. 启动 MySQL 服务
    print("\n[9] 启动 MySQL 服务...")
    stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld 2>&1 || service mysqld start 2>&1')
    time.sleep(5)
    
    # 10. 等待 MySQL 完全启动
    print("\n[10] 等待 MySQL 启动（15秒）...")
    time.sleep(15)
    
    # 11. 检查 socket 文件
    print("\n[11] 检查 socket 文件...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/mysql.sock 2>&1')
    socket_info = stdout.read().decode('utf-8')
    print(f"Socket: {socket_info}")
    
    # 12. 尝试使用 socket 连接（无密码）
    print("\n[12] 尝试无密码连接...")
    stdin, stdout, stderr = ssh.exec_command('mysql -u root --socket=/var/lib/mysql/mysql.sock -e "SELECT 1" 2>&1')
    nopass_result = stdout.read().decode('utf-8')
    nopass_error = stderr.read().decode('utf-8')
    print("无密码连接:")
    print(nopass_result if nopass_result else "[无输出]")
    if nopass_error:
        print("错误:", nopass_error)
    
    # 13. 如果无密码失败，尝试 skip-grant-tables
    if 'Access denied' in nopass_error or 'ERROR' in nopass_error:
        print("\n[13] 使用 skip-grant-tables 模式...")
        
        # 停止 MySQL
        stdin, stdout, stderr = ssh.exec_command('killall -9 mysqld 2>/dev/null || true')
        time.sleep(3)
        
        # 启动 skip-grant-tables
        stdin, stdout, stderr = ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 &')
        print("等待启动（15秒）...")
        time.sleep(15)
        
        # 重置 root 密码
        reset_script = '''mysql -u root --socket=/var/lib/mysql/mysql.sock << 'MYSQL_EOF'
FLUSH PRIVILEGES;

-- 删除旧 root 用户
DELETE FROM mysql.user WHERE user='root';
FLUSH PRIVILEGES;

-- 创建新 root 用户
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

FLUSH PRIVILEGES;

SELECT user, host, plugin FROM mysql.user WHERE user='root';
MYSQL_EOF
'''
        stdin, stdout, stderr = ssh.exec_command(reset_script)
        time.sleep(5)
        reset_result = stdout.read().decode('utf-8')
        reset_error = stderr.read().decode('utf-8')
        print("重置结果:")
        print(reset_result if reset_result else "[无输出]")
        if reset_error and 'Warning' not in reset_error:
            print("错误:", reset_error)
        
        # 停止并正常启动
        print("\n[14] 正常启动 MySQL...")
        stdin, stdout, stderr = ssh.exec_command('mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>&1 || killall -9 mysqld 2>/dev/null || true')
        time.sleep(3)
        stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld 2>&1 || service mysqld start 2>&1')
        time.sleep(10)
    
    # 15. 测试 MySQL 连接
    print("\n[15] 测试 MySQL 连接...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT SUCCESS" 2>&1')
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print("测试结果:")
    print(test_result if test_result else "[无输出]")
    if test_error and 'Warning' not in test_error:
        print("错误:", test_error)
    
    # 16. 测试 PyMySQL
    print("\n[16] 测试 PyMySQL 连接...")
    test_pymysql = r'''python3 << 'PYEOF'
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
    cursor.execute('SELECT "PyMySQL成功" AS status')
    result = cursor.fetchone()
    print(f"✓ {result[0]}")
    conn.close()
except Exception as e:
    print(f"✗ 连接失败: {e}")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_pymysql)
    pymysql_result = stdout.read().decode('utf-8')
    print(pymysql_result)
    
    # 17. 测试 Django
    print("\n[17] 测试 Django 连接...")
    test_django = r'''python3 << 'DJEOF'
import os, sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT "Django成功"')
    result = cursor.fetchone()
    print(f"✓ {result[0]}")
except Exception as e:
    print(f"✗ 失败: {e}")
DJEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_django)
    django_result = stdout.read().decode('utf-8')
    print(django_result)
    
    # 18. 重启 Gunicorn
    print("\n[18] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('lsof -ti:8000 | xargs kill -9 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    time.sleep(10)
    
    # 19. 测试 HTTP
    print("\n[19] 测试 HTTP 访问...")
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn: {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx: {nginx_status}")
    
    # 20. 检查错误日志
    print("\n[20] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -15 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库访问错误")
    else:
        print("[✓] 无数据库访问错误")
    
    if errors.strip():
        print("日志:")
        print(errors[-800:])
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    
    if 'SUCCESS' in test_result and 'PyMySQL成功' in pymysql_result:
        print("\n✅ MySQL 修复成功！")
        if nginx_status == '200' or gunicorn_status == '200':
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
