#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    print("启动MySQL...")
    
    # Kill any existing MySQL processes
    ssh.exec_command('pkill -9 mysqld 2>/dev/null || true')
    time.sleep(2)
    
    # Remove socket file
    ssh.exec_command('rm -f /var/lib/mysql/mysql.sock')
    time.sleep(1)
    
    # Start MySQL with systemd
    print("使用systemctl启动MySQL...")
    stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld')
    time.sleep(10)
    
    # Check status
    stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld')
    status = stdout.read().decode().strip()
    print(f"MySQL状态: {status}")
    
    if status == 'active':
        # Test connection
        print("\n测试MySQL连接...")
        stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT \'OK\' as status;" 2>&1')
        result = stdout.read().decode() + stderr.read().decode()
        print(result.strip())
        
        if 'OK' in result or 'status' in result:
            print("\n✓ MySQL已成功启动并可以连接！")
        else:
            print("\n✗ MySQL启动但无法连接，需要重置密码")
            
            # Reset password
            print("\n重置root密码...")
            ssh.exec_command('systemctl stop mysqld')
            time.sleep(3)
            
            ssh.exec_command('mysqld_safe --skip-grant-tables &')
            time.sleep(10)
            
            reset_cmd = '''mysql -u root <<EOF
FLUSH PRIVILEGES;
DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF'''
            ssh.exec_command(reset_cmd)
            time.sleep(5)
            
            # Restart MySQL normally
            ssh.exec_command('pkill -9 mysqld; sleep 3; systemctl start mysqld')
            time.sleep(10)
            
            # Test again
            stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT \'SUCCESS\';" 2>&1')
            result = stdout.read().decode() + stderr.read().decode()
            print(result.strip())
    else:
        print(f"\n✗ MySQL启动失败，状态: {status}")
        
        # Check error log
        print("\n检查错误日志...")
        stdin, stdout, stderr = ssh.exec_command('tail -20 /var/log/mysqld.log')
        print(stdout.read().decode()[-500:])
    
finally:
    ssh.close()
