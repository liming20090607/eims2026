#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并优化OpenClaw自动修复配置
Check and optimize OpenClaw auto-fix configuration
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    print("=" * 70)
    print("检查OpenClaw配置")
    print("=" * 70)
    
    # 1. Check current health check interval
    print("\n[1] 检查当前健康检查间隔...")
    stdin, stdout, stderr = ssh.exec_command('crontab -l | grep health_check')
    cron_config = stdout.read().decode()
    print(f"当前配置:\n{cron_config}")
    
    # 2. Check MySQL status
    print("\n[2] 检查MySQL当前状态...")
    stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld 2>/dev/null || service mysql status 2>/dev/null || echo "unknown"')
    mysql_status = stdout.read().decode().strip()
    print(f"MySQL状态: {mysql_status}")
    
    # 3. Check if MySQL is actually running
    stdin, stdout, stderr = ssh.exec_command('pgrep mysqld && echo "RUNNING" || echo "NOT_RUNNING"')
    mysql_running = stdout.read().decode().strip()
    print(f"MySQL进程: {mysql_running}")
    
    # 4. Check error logs
    print("\n[3] 检查最近的错误...")
    stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
    errors = stdout.read().decode()
    if errors.strip():
        print(errors[-500:])
    else:
        print("无错误日志")
    
    # 5. Check OpenClaw logs
    print("\n[4] 检查OpenClaw最近的修复记录...")
    stdin, stdout, stderr = ssh.exec_command('tail -10 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null')
    fix_log = stdout.read().decode()
    if fix_log.strip():
        print(fix_log)
    else:
        print("无修复记录")
    
    print("\n" + "=" * 70)
    
finally:
    ssh.close()
