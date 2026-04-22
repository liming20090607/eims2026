#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断MySQL启动问题
Diagnose MySQL startup issues
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    print("=" * 70)
    print("MySQL启动问题诊断")
    print("=" * 70)
    
    # 1. Check MySQL error log
    print("\n[1] 检查MySQL错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/log/mysqld.log 2>/dev/null || tail -30 /var/log/mysql/error.log 2>/dev/null || echo "日志文件不存在"')
    log = stdout.read().decode()
    print(log[-1000:] if len(log) > 1000 else log)
    
    # 2. Check MySQL data directory
    print("\n[2] 检查MySQL数据目录...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/ | head -20')
    print(stdout.read().decode())
    
    # 3. Check disk space
    print("\n[3] 检查磁盘空间...")
    stdin, stdout, stderr = ssh.exec_command('df -h /var/lib/mysql')
    print(stdout.read().decode())
    
    # 4. Check MySQL process
    print("\n[4] 检查MySQL进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysql | grep -v grep')
    processes = stdout.read().decode()
    if processes.strip():
        print(processes)
    else:
        print("MySQL进程未运行")
    
    # 5. Try to start MySQL manually
    print("\n[5] 尝试手动启动MySQL...")
    stdin, stdout, stderr = ssh.exec_command('mysqld_safe --user=mysql &')
    time.sleep(15)
    
    # Check if started
    stdin, stdout, stderr = ssh.exec_command('pgrep mysqld && echo "MySQL已启动" || echo "MySQL启动失败"')
    status = stdout.read().decode().strip()
    print(f"   {status}")
    
    # Check socket
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/lib/mysql/mysql.sock 2>/dev/null && echo "Socket存在" || echo "Socket不存在"')
    socket_status = stdout.read().decode().strip()
    print(f"   {socket_status}")
    
    # 6. If running, test connection
    if "MySQL已启动" in status and "Socket存在" in socket_status:
        print("\n[6] 测试MySQL连接...")
        stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT \'OK\' as status;" 2>&1')
        result = stdout.read().decode() + stderr.read().decode()
        print(f"   {result.strip()}")
    
    # 7. Check MySQL configuration
    print("\n[7] 检查MySQL配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /etc/my.cnf 2>/dev/null || cat /etc/mysql/my.cnf 2>/dev/null || echo "配置文件不存在"')
    config = stdout.read().decode()
    print(config[:500])
    
    print("\n" + "=" * 70)
    
finally:
    ssh.close()
