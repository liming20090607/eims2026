#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用OpenClaw增强脚本修复MySQL
Directly use OpenClaw enhanced script to fix MySQL
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    print("=" * 70)
    print("使用OpenClaw增强脚本修复MySQL")
    print("=" * 70)
    
    # Execute the enhanced fix script that was already created
    print("\n执行OpenClaw增强修复脚本...")
    stdin, stdout, stderr = ssh.exec_command('bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh')
    
    print("等待修复完成（约60秒）...")
    for i in range(30):
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command('pgrep -f enhanced_mysql_fix | wc -l')
        running = int(stdout.read().decode().strip())
        if running == 0:
            print(f"✓ 修复脚本已完成（{i*2}秒）")
            break
        if i % 5 == 0:
            print(f"  修复进行中... ({i*2}秒)")
    
    # Check the log
    print("\n查看修复日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /root/.openclaw/monitoring/logs/auto_fix.log')
    log = stdout.read().decode()
    print(log)
    
    # Verify MySQL
    print("\n验证MySQL连接...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT \'SUCCESS\' as status;" 2>&1')
    result = stdout.read().decode() + stderr.read().decode()
    print(result.strip())
    
    # Restart Gunicorn
    print("\n重启Gunicorn...")
    ssh.exec_command('pkill -9 -f gunicorn; sleep 2; cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &')
    time.sleep(5)
    
    # Final check
    print("\n最终检查...")
    checks = [
        ('MySQL', 'mysql -uroot -pEIMS2026_mysql -e "SELECT 1;" 2>&1 | grep -i error || echo OK'),
        ('Gunicorn', 'ps aux | grep "[g]unicorn" | wc -l'),
        ('HTTP', 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/'),
    ]
    
    for name, cmd in checks:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode().strip()
        print(f"{name}: {result}")
    
    print("\n" + "=" * 70)
    print("修复完成！")
    print("=" * 70)
    
finally:
    ssh.close()
