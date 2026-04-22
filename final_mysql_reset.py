#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终MySQL密码重置方案
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*60)
    print("MySQL密码重置 - 最终方案")
    print("="*60)
    
    print("\n连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    # 步骤1：查找MySQL的socket文件
    print("\n[步骤1] 查找MySQL socket文件...")
    stdin, stdout, stderr = ssh.exec_command("find /tmp -name 'mysql.sock' 2>/dev/null; find /var/lib/mysql -name 'mysql.sock' 2>/dev/null; find /www/server/mysql -name 'mysql.sock' 2>/dev/null")
    socket_path = stdout.read().decode('utf-8', errors='ignore').strip().split('\n')[0]
    print("Socket文件: {}".format(socket_path if socket_path else "未找到"))
    
    # 步骤2：停止MySQL
    print("\n[步骤2] 停止MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl stop mysqld")
    time.sleep(3)
    print("MySQL已停止")
    
    # 步骤3：创建初始化文件
    print("\n[步骤3] 创建密码重置文件...")
    init_sql = "ALTER USER 'root'@'localhost' IDENTIFIED BY 'EIMS2026_mysql';\nFLUSH PRIVILEGES;\n"
    stdin, stdout, stderr = ssh.exec_command("echo '{}' > /tmp/mysql-init.sql".format(init_sql.replace("'", "\\'")))
    time.sleep(1)
    print("初始化文件已创建")
    
    # 步骤4：以init-file模式启动MySQL
    print("\n[步骤4] 使用init-file启动MySQL...")
    if socket_path:
        init_cmd = "mysqld --init-file=/tmp/mysql-init.sql --user=mysql &"
    else:
        init_cmd = "mysqld --init-file=/tmp/mysql-init.sql --user=mysql &"
    
    stdin, stdout, stderr = ssh.exec_command(init_cmd)
    time.sleep(8)
    print("MySQL正在启动...")
    
    # 步骤5：验证连接
    print("\n[步骤5] 验证MySQL密码...")
    time.sleep(2)
    
    # 尝试多种连接方式
    test_commands = [
        ("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 as test;'", "新密码"),
        ("mysql -uroot -e 'SELECT 1 as test;'", "空密码"),
    ]
    
    success = False
    for cmd, label in test_commands:
        print("\n尝试 {}...".format(label))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if 'test' in result:
            print("[SUCCESS] {}连接成功！".format(label))
            success = True
            
            if label == "新密码":
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
            else:
                print("使用空密码，请在 deploy_config.py 中设置 MYSQL_PASSWORD = \"\"")
            
            # 显示数据库
            print("\n数据库列表:")
            if label == "新密码":
                stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SHOW DATABASES;'")
            else:
                stdin, stdout, stderr = ssh.exec_command("mysql -uroot -e 'SHOW DATABASES;'")
            db_list = stdout.read().decode('utf-8', errors='ignore')
            print(db_list)
            break
        else:
            print("[FAIL] {}失败".format(label))
            if error:
                print("错误: {}".format(error[:100]))
    
    if not success:
        print("\n[ERROR] 所有连接方式都失败了")
        print("请手动登录宝塔面板查看MySQL密码:")
        print("1. 访问: http://39.106.41.239:8888/login")
        print("2. 用户名: 6616b016")
        print("3. 密码: cdc190aa543b")
        print("4. 点击左侧'数据库' -> 顶部'root密码'")
    
    # 清理临时文件
    ssh.exec_command("rm -f /tmp/mysql-init.sql")
    
    ssh.close()
    
    print("\n" + "="*60)
    if success:
        print("部署准备完成！")
        print("现在可以运行: python auto_deploy.py")
    print("="*60)
    
except Exception as e:
    print("\n错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
