import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("检查 MySQL 连接和权限...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前 settings.py 的数据库配置
    print("\n[1] 检查 /var/www/eims/settings.py 数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES" /var/www/eims/settings.py | head -15')
    db_config = stdout.read().decode('utf-8')
    print(db_config)
    
    # 2. 测试 MySQL 命令行连接
    print("\n[2] 测试 MySQL 连接...")
    
    # 使用 EIMS2026_mysql 密码连接
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT USER(), CURRENT_USER();" 2>&1')
    output1 = stdout.read().decode('utf-8')
    error1 = stderr.read().decode('utf-8')
    
    if 'root@localhost' in output1:
        print("[✓] MySQL 连接成功（密码: EIMS2026_mysql）")
        print(output1)
    else:
        print("[✗] 使用 EIMS2026_mysql 连接失败")
        print("错误:", error1[:200] if error1 else output1)
    
    # 3. 检查 MySQL 用户权限
    print("\n[3] 检查 MySQL root 用户权限...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT user, host, authentication_string FROM mysql.user WHERE user=\'root\';" 2>&1')
    user_info = stdout.read().decode('utf-8')
    print(user_info)
    
    # 4. 重置 MySQL root 密码
    print("\n[4] 重置 MySQL root 用户密码...")
    
    reset_mysql_script = '''
mysql -uroot -pEIMS2026_mysql << 'MYSQL_EOF'
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
SELECT 'Password reset successful' AS status;
MYSQL_EOF
'''
    
    stdin, stdout, stderr = ssh.exec_command(reset_mysql_script)
    reset_output = stdout.read().decode('utf-8')
    reset_error = stderr.read().decode('utf-8')
    print(reset_output)
    if reset_error:
        print("错误:", reset_error[:200])
    
    # 5. 再次测试连接
    print("\n[5] 验证密码重置后的连接...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql eims -e "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema=\'eims\';" 2>&1')
    verify_output = stdout.read().decode('utf-8')
    verify_error = stderr.read().decode('utf-8')
    
    if 'table_count' in verify_output:
        print("[✓] 数据库连接验证成功")
        print(verify_output)
    else:
        print("[✗] 连接验证失败")
        print("错误:", verify_error[:200] if verify_error else verify_output)
    
    # 6. 检查是否有多个 MySQL 实例
    print("\n[6] 检查 MySQL 服务状态...")
    stdin, stdout, stderr = ssh.exec_command('systemctl status mysqld 2>&1 | head -10')
    mysql_status = stdout.read().decode('utf-8')
    print(mysql_status)
    
    # 7. 检查 /etc/my.cnf 配置
    print("\n[7] 检查 MySQL 配置文件...")
    stdin, stdout, stderr = ssh.exec_command('cat /etc/my.cnf 2>/dev/null || cat /etc/mysql/my.cnf 2>/dev/null || echo "未找到配置文件"')
    mysql_config = stdout.read().decode('utf-8')
    if mysql_config and '未找到' not in mysql_config:
        print(mysql_config[:500])
    
    # 8. 检查是否有密码策略
    print("\n[8] 检查 MySQL 密码策略...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SHOW VARIABLES LIKE \'validate_password%\';" 2>&1')
    password_policy = stdout.read().decode('utf-8')
    print(password_policy)
    
    print("\n" + "="*70)
    print("诊断完成")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
