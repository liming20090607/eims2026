#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取宝塔面板MySQL密码
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    # 方法1：尝试从宝塔配置文件读取
    print("尝试方法1：读取宝塔配置文件...")
    stdin, stdout, stderr = ssh.exec_command('cat /www/server/panel/data/mysql_root.txt')
    mysql_pwd = stdout.read().decode('utf-8', errors='ignore').strip()
    if mysql_pwd:
        print("MySQL root密码: {}".format(mysql_pwd))
    else:
        # 方法2：使用宝塔命令修改并显示密码
        print("\n方法1失败，尝试方法2：使用bt命令...")
        stdin, stdout, stderr = ssh.exec_command("echo 'password' | bt")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
        # 方法3：直接重置MySQL密码为一个已知值
        print("\n方法3：重置MySQL密码为 EIMS2026_mysql_root")
        stdin, stdout, stderr = ssh.exec_command("mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY 'EIMS2026_mysql_root'; FLUSH PRIVILEGES;\"")
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if error:
            print("重置失败: {}".format(error))
        else:
            print("MySQL密码已成功重置为: EIMS2026_mysql_root")
            print("\n请更新 deploy_config.py 中的 MYSQL_PASSWORD 为: EIMS2026_mysql_root")
    
    ssh.close()
    
except Exception as e:
    print("错误: {}".format(str(e)))
