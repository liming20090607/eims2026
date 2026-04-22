#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证MySQL密码并更新配置
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    # 验证MySQL密码
    print("\n验证MySQL连接（密码: EIMS2026_mysql）...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 as test;'")
    verify_output = stdout.read().decode('utf-8', errors='ignore')
    verify_error = stderr.read().decode('utf-8', errors='ignore')
    
    print("输出: {}".format(verify_output))
    
    if 'test' in verify_output:
        print("\n[OK] MySQL密码验证成功！")
        print("[OK] 密码: EIMS2026_mysql")
        
        # 更新deploy_config.py
        print("\n正在更新 deploy_config.py...")
        with open('deploy_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            "MYSQL_PASSWORD = \"your_mysql_password\"  # 服务器MySQL密码",
            "MYSQL_PASSWORD = \"EIMS2026_mysql\"  # 服务器MySQL密码"
        )
        
        with open('deploy_config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] deploy_config.py 已更新")
        print("\n" + "="*60)
        print("现在可以运行部署脚本了:")
        print("python auto_deploy.py")
        print("="*60)
    else:
        print("[ERROR] 验证失败")
        print("错误: {}".format(verify_error))
    
    ssh.close()
    
except Exception as e:
    print("错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
