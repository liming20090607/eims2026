#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
强制重置MySQL密码 - 使用skip-grant-tables方法
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*60)
    print("开始重置MySQL root密码")
    print("="*60)
    
    print("\n连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    # 步骤1：停止MySQL服务
    print("\n[1/6] 停止MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl stop mysqld")
    time.sleep(2)
    print("MySQL服务已停止")
    
    # 步骤2：以skip-grant-tables模式启动MySQL
    print("\n[2/6] 以无密码模式启动MySQL...")
    stdin, stdout, stderr = ssh.exec_command("mysqld_safe --skip-grant-tables --skip-networking &")
    time.sleep(5)
    print("MySQL已启动（无密码模式）")
    
    # 步骤3：连接MySQL并重置密码
    print("\n[3/6] 连接MySQL并重置密码...")
    mysql_commands = """
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
exit;
"""
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot")
    stdin.write(mysql_commands)
    stdin.flush()
    time.sleep(3)
    result = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print("执行结果: {}".format(result if result else "无输出"))
    if error:
        print("警告: {}".format(error))
    
    # 步骤4：停止无密码模式的MySQL
    print("\n[4/6] 停止无密码模式的MySQL...")
    stdin, stdout, stderr = ssh.exec_command("mysqladmin -uroot shutdown")
    time.sleep(3)
    print("MySQL已停止")
    
    # 步骤5：正常启动MySQL
    print("\n[5/6] 正常启动MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl start mysqld")
    time.sleep(5)
    print("MySQL服务已启动")
    
    # 步骤6：验证密码
    print("\n[6/6] 验证MySQL密码...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 as test; SHOW DATABASES;'"
)
    verify_output = stdout.read().decode('utf-8', errors='ignore')
    verify_error = stderr.read().decode('utf-8', errors='ignore')
    
    print("\n验证输出:")
    print(verify_output)
    
    if 'test' in verify_output:
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
        print("\n" + "="*60)
        print("现在可以运行部署脚本了:")
        print("python auto_deploy.py")
        print("="*60)
    else:
        print("\n[ERROR] 验证失败")
        if verify_error:
            print("错误信息: {}".format(verify_error))
    
    ssh.close()
    
except Exception as e:
    print("\n错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
