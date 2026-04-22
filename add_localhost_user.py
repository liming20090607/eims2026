import paramiko
import time

print("="*70)
print("MySQL localhost 用户修复")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 添加 root@localhost 用户
    print("\n[1] 添加 root@localhost 用户...")
    create_user_cmd = '''mysql -uroot -pEIMS2026_mysql -h 127.0.0.1 << 'EOF'
CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT User, Host, plugin FROM mysql.user WHERE User='root';
EOF
'''
    stdin, stdout, stderr = ssh.exec_command(create_user_cmd)
    time.sleep(5)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print("执行结果:")
    if result.strip():
        print(result)
    if error.strip():
        print("警告:", error.strip()[:300])
    
    # 2. 测试 localhost 连接
    print("\n[2] 测试 localhost 连接...")
    stdin, stdout, stderr = ssh.exec_command('''mysql -uroot -pEIMS2026_mysql -h localhost -e "SELECT 'SUCCESS_LOCALHOST' AS test;" 2>&1''')
    local_result = stdout.read().decode('utf-8')
    local_error = stderr.read().decode('utf-8')
    
    if 'SUCCESS_LOCALHOST' in local_result:
        print("✓ localhost 连接成功")
    else:
        print("✗ localhost 连接失败")
        if local_error:
            print("错误:", local_error.strip()[:200])
    
    # 3. 重启 Gunicorn 确保使用新连接
    print("\n[3] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn || true')
    time.sleep(3)
    
    # 清空日志
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 启动 Gunicorn
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    ssh.exec_command(start_cmd)
    
    print("等待 10 秒...")
    time.sleep(10)
    
    # 4. 测试 HTTP
    print("\n[4] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print("Gunicorn (8000): " + gunicorn_status)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print("Nginx (80): " + nginx_status)
    
    # 5. 检查错误日志
    print("\n[5] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] 仍有数据库访问错误")
        print(errors[-1000:])
    else:
        print("[OK] 无数据库访问错误")
    
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)
    
    if gunicorn_status == '200' and nginx_status == '200':
        print("\n[OK] 服务正常运行！")
        print("\n现在可以尝试登录:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n[警告] 服务状态异常")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
