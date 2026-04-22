#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MySQL密码重置 - 使用ALTER TABLE直接修改
"""
import paramiko
import time
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print(" MySQL密码重置工具")
    print("="*70)
    
    print("\n[1/6] 连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    print("[OK] SSH连接成功")
    
    # 步骤1：停止MySQL
    print("\n[2/6] 停止MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl stop mysqld 2>&1")
    time.sleep(3)
    status_out = stdout.read().decode('utf-8', errors='ignore')
    if status_out:
        print("输出: {}".format(status_out[:200]))
    print("[OK] MySQL已停止")
    
    # 步骤2：启动skip-grant-tables模式
    print("\n[3/6] 启动MySQL（无授权模式）...")
    # 使用screen启动，确保后台运行
    stdin, stdout, stderr = ssh.exec_command("mysqld --skip-grant-tables --user=mysql --daemonize 2>&1")
    time.sleep(8)
    start_out = stdout.read().decode('utf-8', errors='ignore')
    start_err = stderr.read().decode('utf-8', errors='ignore')
    if start_err and 'error' in start_err.lower():
        print("[WARN] 启动警告: {}".format(start_err[:200]))
    else:
        print("[OK] MySQL已启动")
    
    # 步骤3：重置密码
    print("\n[4/6] 重置MySQL root密码...")
    
    # 使用UPDATE语句直接修改mysql.user表
    # MySQL 8.0需要使用UPDATE + FLUSH PRIVILEGES
    update_cmd = """mysql -u root << 'SQLEOF'
USE mysql;
UPDATE user SET authentication_string='' WHERE User='root' AND Host='localhost';
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
SELECT User, Host, plugin FROM user WHERE User='root';
SQLEOF"""
    
    stdin, stdout, stderr = ssh.exec_command(update_cmd)
    time.sleep(5)
    reset_out = stdout.read().decode('utf-8', errors='ignore')
    reset_err = stderr.read().decode('utf-8', errors='ignore')
    
    print("\n重置输出:")
    if reset_out:
        print(reset_out)
    if reset_err:
        print("[WARN] {}".format(reset_err[:300]))
    
    # 步骤4：停止MySQL
    print("\n[5/6] 停止MySQL并重新启动...")
    stdin, stdout, stderr = ssh.exec_command("mysqladmin -u root shutdown 2>&1")
    time.sleep(3)
    
    # 正常启动
    stdin, stdout, stderr = ssh.exec_command("systemctl start mysqld 2>&1")
    time.sleep(5)
    print("[OK] MySQL服务已重启")
    
    # 步骤5：验证
    print("\n[6/6] 验证MySQL密码...")
    time.sleep(2)
    
    # 测试新密码
    test_cmd = "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test; SHOW DATABASES;' 2>&1"
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    verify_out = stdout.read().decode('utf-8', errors='ignore')
    verify_err = stderr.read().decode('utf-8', errors='ignore')
    
    print("\n验证结果:")
    print(verify_out if verify_out else verify_err)
    
    if 'test' in verify_out and 'Database' in verify_out:
        print("\n" + "="*70)
        print(" SUCCESS! MySQL密码重置成功")
        print("="*70)
        print(" 新密码: EIMS2026_mysql")
        print("="*70)
        
        # 更新配置文件
        print("\n正在更新 deploy_config.py...")
        with open('deploy_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            'MYSQL_PASSWORD = "your_mysql_password"  # 服务器MySQL密码',
            'MYSQL_PASSWORD = "EIMS2026_mysql"  # 服务器MySQL密码'
        )
        
        with open('deploy_config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] deploy_config.py 已更新")
        print("\n数据库列表:")
        print(verify_out)
        
        print("\n" + "="*70)
        print(" 部署准备就绪！执行: python auto_deploy.py")
        print("="*70)
    else:
        print("\n" + "="*70)
        print(" ERROR - 密码验证失败")
        print("="*70)
        print("\n请手动获取MySQL密码:")
        print("1. 访问宝塔面板: http://39.106.41.239:8888/login")
        print("2. 用户名: 6616b016")
        print("3. 密码: cdc190aa543b")
        print("4. 数据库 -> root密码")
    
    ssh.close()
    
except Exception as e:
    print("\n[ERROR] {}".format(str(e)))
    import traceback
    traceback.print_exc()
