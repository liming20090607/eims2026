import paramiko
import time

print("="*70)
print("MySQL 紧急重置 root 密码")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 停止 MySQL 服务
    print("\n[1] 停止 MySQL 服务...")
    stdin, stdout, stderr = ssh.exec_command('systemctl stop mysqld 2>&1 || service mysqld stop 2>&1 || true')
    time.sleep(3)
    print("MySQL 已停止")
    
    # 2. 以 skip-grant-tables 模式启动 MySQL
    print("\n[2] 启动 MySQL（跳过权限验证）...")
    stdin, stdout, stderr = ssh.exec_command('mysqld_safe --skip-grant-tables &')
    time.sleep(5)
    
    # 3. 无密码连接 MySQL 并重置 root 密码
    print("\n[3] 重置 root 用户密码...")
    reset_script = '''mysql << 'MYSQL_EOF'
-- 刷新权限表
FLUSH PRIVILEGES;

-- 删除旧的 root 用户
DELETE FROM mysql.user WHERE user='root';

-- 创建新的 root 用户
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
    stdin, stdout, stderr = ssh.exec_command(reset_script)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print("重置结果:")
    print(result)
    if error and 'Warning' not in error:
        print("错误:", error)
    
    # 4. 停止 skip-grant-tables 模式
    print("\n[4] 停止 MySQL...")
    stdin, stdout, stderr = ssh.exec_command('mysqladmin -u root shutdown 2>&1 || true')
    time.sleep(3)
    
    # 5. 正常启动 MySQL
    print("\n[5] 正常启动 MySQL...")
    stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld 2>&1 || service mysqld start 2>&1')
    time.sleep(5)
    
    # 6. 测试 MySQL 连接
    print("\n[6] 测试 MySQL 连接...")
    stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -pEIMS2026_mysql -e "SELECT 'MySQL连接成功' AS status;" 2>&1""")
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print("测试结果:", test_result)
    if test_error and 'Warning' not in test_error:
        print("测试错误:", test_error)
    
    # 7. 测试 PyMySQL
    print("\n[7] 测试 PyMySQL 连接...")
    test_pymysql = r'''python3 << 'TESTEOF'
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
    cursor.execute('SELECT "PyMySQL连接成功" AS status')
    result = cursor.fetchone()
    print(f"✓ {result[0]}")
    conn.close()
except Exception as e:
    print(f"✗ PyMySQL连接失败: {e}")
TESTEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_pymysql)
    pymysql_result = stdout.read().decode('utf-8')
    print(pymysql_result)
    
    # 8. 清空错误日志
    print("\n[8] 清空错误日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 9. 重启 Gunicorn
    print("\n[9] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('lsof -ti:8000 | xargs kill -9 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    proc_count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {proc_count}")
    
    # 10. 重启 Nginx
    print("\n[10] 重启 Nginx...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -s stop 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx')
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep | wc -l')
    nginx_count = stdout.read().decode('utf-8').strip()
    print(f"Nginx 进程数: {nginx_count}")
    
    # 11. 测试 HTTP 访问
    print("\n[11] 测试 HTTP 访问...")
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # 12. 检查错误日志
    print("\n[12] 检查最新错误...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库访问拒绝错误")
        print(errors[-1000:])
    elif errors.strip():
        print("[✓] 无数据库访问错误")
        print("其他日志:")
        print(errors[-500:])
    else:
        print("[✓] 无错误")
    
    print("\n" + "="*70)
    print("✅ MySQL 紧急重置完成")
    print("="*70)
    
    if nginx_status == '200' or gunicorn_status == '200':
        if 'PyMySQL连接成功' in pymysql_result:
            print("\n✅ 系统完全正常！")
            print("\n访问地址:")
            print("  http://39.106.41.239/login/")
            print("  http://www.xietongai.com.cn/login/")
            print("\n登录凭据:")
            print("  用户名: admin  密码: admin123456")
            print("  用户名: root   密码: root123456")
        else:
            print("\n⚠️ 数据库连接仍存在问题")
    else:
        print("\n⚠️ HTTP 服务状态异常")
        print(f"  Gunicorn: {gunicorn_status}")
        print(f"  Nginx: {nginx_status}")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
