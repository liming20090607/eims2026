#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用宝塔面板工具重置MySQL密码
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*60)
    print("使用宝塔面板工具重置MySQL密码")
    print("="*60)
    
    print("\n连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    # 方法1：使用宝塔的mysql_root.sh脚本
    print("\n[方法1] 使用宝塔mysql_root.sh脚本...")
    stdin, stdout, stderr = ssh.exec_command("bash /www/server/panel/script/mysql_root.sh EIMS2026_mysql")
    time.sleep(5)
    result1 = stdout.read().decode('utf-8', errors='ignore')
    error1 = stderr.read().decode('utf-8', errors='ignore')
    print("输出: {}".format(result1))
    if error1:
        print("警告: {}".format(error1))
    
    # 等待MySQL重启
    print("\n等待MySQL服务重启...")
    time.sleep(5)
    
    # 验证密码
    print("\n[验证] 测试MySQL连接...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 as test;'"
)
    verify_output = stdout.read().decode('utf-8', errors='ignore')
    verify_error = stderr.read().decode('utf-8', errors='ignore')
    
    print("输出: {}".format(verify_output))
    
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
        
        # 方法2：尝试查看宝塔是否有记录MySQL密码
        print("\n[方法2] 查看宝塔面板的MySQL配置...")
        stdin, stdout, stderr = ssh.exec_command("find /www/server/panel -name '*.pl' -o -name '*.json' | xargs grep -l 'mysql' 2>/dev/null | head -5")
        files = stdout.read().decode('utf-8', errors='ignore').strip()
        print("找到的配置文件: {}".format(files))
        
        if files:
            for f in files.split('\n')[:3]:
                print("\n读取: {}".format(f))
                stdin, stdout, stderr = ssh.exec_command("cat {}".format(f))
                content = stdout.read().decode('utf-8', errors='ignore')
                print(content[:300])
    
    ssh.close()
    
except Exception as e:
    print("\n错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
