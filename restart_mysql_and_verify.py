#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重启MySQL服务并验证密码
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    # 检查MySQL服务状态
    print("\n检查MySQL服务状态...")
    stdin, stdout, stderr = ssh.exec_command("systemctl status mysqld 2>/dev/null || systemctl status mysql 2>/dev/null || ps aux | grep mysql")
    status_output = stdout.read().decode('utf-8', errors='ignore')
    print(status_output[:500])
    
    # 重启MySQL服务
    print("\n重启MySQL服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart mysqld 2>/dev/null || systemctl restart mysql 2>/dev/null || /etc/init.d/mysqld restart 2>/dev/null")
    time.sleep(5)
    restart_output = stdout.read().decode('utf-8', errors='ignore')
    restart_error = stderr.read().decode('utf-8', errors='ignore')
    print("输出: {}".format(restart_output))
    if restart_error:
        print("警告: {}".format(restart_error))
    
    # 等待MySQL启动
    print("\n等待MySQL启动...")
    time.sleep(3)
    
    # 验证MySQL密码
    print("\n验证MySQL连接（密码: EIMS2026_mysql）...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 as test; SHOW DATABASES;'")
    verify_output = stdout.read().decode('utf-8', errors='ignore')
    verify_error = stderr.read().decode('utf-8', errors='ignore')
    
    print("输出:")
    print(verify_output)
    
    if 'test' in verify_output and 'Database' in verify_output:
        print("\n[OK] MySQL验证成功！")
        print("[OK] 密码: EIMS2026_mysql")
        print("\n数据库列表:")
        print(verify_output)
        
        # 更新deploy_config.py
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
            print("错误: {}".format(verify_error))
    
    ssh.close()
    
except Exception as e:
    print("错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
