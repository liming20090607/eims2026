#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看宝塔面板MySQL信息
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("连接到服务器...")
    ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
    
    print("\n[1] 查看宝塔面板版本...")
    stdin, stdout, stderr = ssh.exec_command("cat /www/server/panel/version.pl")
    print("宝塔版本: {}".format(stdout.read().decode('utf-8', errors='ignore')))
    
    print("\n[2] 查看MySQL安装路径...")
    stdin, stdout, stderr = ssh.exec_command("ls -la /www/server/ | grep -E 'mysql|mariadb'")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n[3] 查看MySQL配置文件...")
    stdin, stdout, stderr = ssh.exec_command("cat /etc/my.cnf 2>/dev/null | head -20")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n[4] 查找MySQL的socket文件...")
    stdin, stdout, stderr = ssh.exec_command("find / -name 'mysql.sock' 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n[5] 查找宝塔的MySQL密码记录文件...")
    stdin, stdout, stderr = ssh.exec_command("find /www/server/panel -type f -name '*.pl' -o -name '*.txt' -o -name '*.json' 2>/dev/null | head -20")
    files = stdout.read().decode('utf-8', errors='ignore').strip().split('\n')
    for f in files[:10]:
        print("\n文件: {}".format(f))
        stdin, stdout, stderr = ssh.exec_command("cat {}".format(f))
        content = stdout.read().decode('utf-8', errors='ignore')
        print("内容: {}".format(content[:200]))
    
    print("\n[6] 查看MySQL服务状态...")
    stdin, stdout, stderr = ssh.exec_command("systemctl status mysqld | head -15")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    print("\n[7] 查看MySQL错误日志...")
    stdin, stdout, stderr = ssh.exec_command("tail -20 /var/log/mysqld.log 2>/dev/null || tail -20 /www/server/data/*.err 2>/dev/null")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    ssh.close()
    
except Exception as e:
    print("错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
