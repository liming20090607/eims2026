#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可靠的MySQL密码重置脚本
使用--skip-grant-tables方法
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*60)
    print("MySQL密码重置 - 可靠方法")
    print("="*60)
    
    print("\n[1/7] 连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    print("[OK] 连接成功")
    
    # 步骤1：停止MySQL
    print("\n[2/7] 停止MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl stop mysqld")
    time.sleep(3)
    print("[OK] MySQL已停止")
    
    # 步骤2：启动skip-grant-tables模式
    print("\n[3/7] 启动无授权表模式...")
    # 使用nohup后台启动，避免阻塞
    stdin, stdout, stderr = ssh.exec_command("nohup mysqld --skip-grant-tables --user=mysql > /dev/null 2>&1 &")
    time.sleep(5)
    print("[OK] MySQL已启动（无授权模式）")
    
    # 步骤3：使用空密码连接并重置密码
    print("\n[4/7] 重置root密码...")
    
    # 创建一个SQL脚本文件
    reset_sql = """FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
"""
    
    # 写入SQL文件
    stdin, stdout, stderr = ssh.exec_command("cat > /tmp/reset_mysql.sql << 'EOF'\n{}\nEOF".format(reset_sql))
    time.sleep(1)
    
    # 执行SQL
    stdin, stdout, stderr = ssh.exec_command("mysql < /tmp/reset_mysql.sql")
    time.sleep(2)
    result = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if error:
        print("[WARN] 警告: {}".format(error[:200]))
    else:
        print("[OK] SQL执行完成")
    
    # 步骤4：关闭无授权模式的MySQL
    print("\n[5/7] 关闭无授权模式的MySQL...")
    stdin, stdout, stderr = ssh.exec_command("mysqladmin -uroot shutdown")
    time.sleep(3)
    print("[OK] MySQL已关闭")
    
    # 步骤5：正常启动MySQL
    print("\n[6/7] 正常启动MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl start mysqld")
    time.sleep(5)
    print("[OK] MySQL服务已启动")
    
    # 步骤6：验证密码
    print("\n[7/7] 验证MySQL密码...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 as connection_test; SHOW DATABASES;'")
    verify_output = stdout.read().decode('utf-8', errors='ignore')
    verify_error = stderr.read().decode('utf-8', errors='ignore')
    
    print("\n执行结果:")
    print(verify_output)
    
    if 'connection_test' in verify_output:
        print("\n" + "="*60)
        print("[SUCCESS] MySQL密码重置成功！")
        print("[SUCCESS] 新密码: EIMS2026_mysql")
        print("="*60)
        
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
        
        # 显示数据库列表
        print("\n现有数据库列表:")
        print(verify_output)
        
        print("\n" + "="*60)
        print("部署准备就绪！")
        print("请执行: python auto_deploy.py")
        print("="*60)
    else:
        print("\n[ERROR] 密码验证失败")
        if verify_error:
            print("错误信息: {}".format(verify_error))
        print("\n请手动登录宝塔面板查看MySQL密码:")
        print("1. 访问: http://39.106.41.239:8888/login")
        print("2. 用户名: 6616b016")
        print("3. 密码: cdc190aa543b")
        print("4. 左侧菜单: 数据库 -> root密码")
    
    # 清理临时文件
    ssh.exec_command("rm -f /tmp/reset_mysql.sql")
    
    ssh.close()
    
except Exception as e:
    print("\n[ERROR] 发生错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
