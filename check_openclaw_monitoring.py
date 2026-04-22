#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check OpenClaw monitoring logs for MySQL issues
"""
import paramiko
import time

print("=" * 70)
print("Checking OpenClaw Monitoring Logs")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    print("SSH Connected\n")
    
    # Check OpenClaw health check logs
    print("[1] OpenClaw Health Check Logs (last 30 lines):")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null')
    health_log = stdout.read().decode()
    print(health_log if health_log else "No health check logs found")
    
    # Check OpenClaw auto-fix logs
    print("\n[2] OpenClaw Auto-Fix Logs (last 30 lines):")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null')
    fix_log = stdout.read().decode()
    print(fix_log if fix_log else "No auto-fix logs found")
    
    # Check if OpenClaw detected MySQL issues
    print("\n[3] Searching for MySQL-related entries:")
    stdin, stdout, stderr = ssh.exec_command('grep -i mysql /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null | tail -10')
    mysql_entries = stdout.read().decode()
    print(mysql_entries if mysql_entries else "No MySQL entries found")
    
    # Check current MySQL status
    print("\n[4] Current MySQL Status:")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" 2>&1')
    time.sleep(2)
    mysql_status = stdout.read().decode() + stderr.read().decode()
    print(mysql_status)
    
    # Check if OpenClaw monitoring script is running
    print("\n[5] OpenClaw Monitoring Processes:")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep -E "openclaw|health_check|auto_fix" | grep -v grep')
    monitoring_ps = stdout.read().decode()
    print(monitoring_ps if monitoring_ps else "No monitoring processes running")
    
    # Check crontab for monitoring tasks
    print("\n[6] Monitoring Crontab:")
    stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep -i "health_check\|auto_fix\|openclaw"')
    cron_tasks = stdout.read().decode()
    print(cron_tasks if cron_tasks else "No monitoring cron tasks found")
    
    print("\n" + "=" * 70)
    print("OpenClaw Monitoring Check Complete")
    print("=" * 70)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
