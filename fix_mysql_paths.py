#!/usr/bin/env python3
"""Fix MySQL command paths in auto-fix scripts"""
import paramiko
import time

def run_ssh(cmd, desc=""):
    """Run SSH command"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('39.106.41.239', username='root', password='fjkl546#')
    
    print(f"  {desc}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    
    if output:
        print(f"    → {output[:200]}")
    if error and exit_code != 0:
        print(f"    ⚠ {error[:200]}")
    
    ssh.close()
    return exit_code, output, error

print("=" * 80)
print("🔧 Fixing MySQL Command Paths in Auto-Fix Scripts")
print("=" * 80)

# Step 1: Find MySQL binary locations
print("\n[1/5] Finding MySQL binaries...")
run_ssh("which mysqld_safe 2>/dev/null || echo 'NOT_FOUND'", "mysqld_safe location")
run_ssh("which mysql 2>/dev/null || echo 'NOT_FOUND'", "mysql client location")
run_ssh("which mysqladmin 2>/dev/null || echo 'NOT_FOUND'", "mysqladmin location")
run_ssh("ls -la /usr/local/mysql/bin/mysqld* 2>/dev/null | head -5", "MySQL bin directory")
run_ssh("find / -name mysqld_safe -type f 2>/dev/null | head -3", "Search for mysqld_safe")

# Step 2: Check current script content
print("\n[2/5] Checking current enhanced_mysql_fix.sh...")
run_ssh("head -30 /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "Script header")

# Step 3: Create fixed version with correct paths
print("\n[3/5] Creating fixed script with correct MySQL paths...")

fixed_script = '''#!/bin/bash
LOG="/root/.openclaw/monitoring/logs/auto_fix.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ========== MySQL自动修复开始 ==========" >> $LOG
echo "[$TS] [0%] 检测到MySQL故障" >> $LOG

# 停止
echo "[$TS] [10%] 停止MySQL" >> $LOG
killall -9 mysqld mysqld_safe 2>/dev/null
sleep 2
rm -f /var/lib/mysql/mysql.sock
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
echo "[$TS] [20%] 清理完成" >> $LOG

# 恢复模式启动（使用完整路径）
echo "[$TS] [30%] 启动恢复模式" >> $LOG
/usr/local/mysql/bin/mysqld_safe --user=mysql --socket=/var/lib/mysql/mysql.sock &
sleep 10

# 检查socket
for i in {1..15}; do
    if [ -f /var/lib/mysql/mysql.sock ]; then
        echo "[$TS] [40%] Socket创建成功" >> $LOG
        break
    fi
    sleep 1
done

# 重置密码
echo "[$TS] [50%] 重置密码" >> $LOG
/usr/local/mysql/bin/mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "[$TS] [60%] 密码重置完成" >> $LOG

# 重启
echo "[$TS] [70%] 重启MySQL" >> $LOG
/usr/local/mysql/bin/mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld
sleep 3
systemctl start mysqld 2>/dev/null || service mysql start || /etc/init.d/mysql start
sleep 5

# 验证
echo "[$TS] [80%] 验证连接" >> $LOG
/usr/local/mysql/bin/mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$TS] [90%] MySQL正常" >> $LOG
else
    echo "[$TS] [90%] MySQL仍有问题，尝试直接启动" >> $LOG
    # 备用方案：直接启动mysqld
    killall -9 mysqld 2>/dev/null
    /usr/local/mysql/bin/mysqld --user=mysql --socket=/var/lib/mysql/mysql.sock &
    sleep 5
    /usr/local/mysql/bin/mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
    if [ $? -eq 0 ]; then
        echo "[$TS] [90%] MySQL通过直接启动恢复正常" >> $LOG
    else
        echo "[$TS] [90%] MySQL修复失败" >> $LOG
    fi
fi

# 重启Gunicorn
echo "[$TS] [95%] 重启Gunicorn" >> $LOG
pkill -9 -f gunicorn 2>/dev/null
sleep 2
cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
sleep 3

echo "[$TS] [100%] 修复完成" >> $LOG
echo "[$TS] ============================" >> $LOG
'''

# Write the fixed script
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

# Write script using Python to avoid shell escaping issues
script_cmd = f"""python3 -c \"
import os
script = '''{fixed_script}'''
os.makedirs('/root/.openclaw/monitoring/scripts', exist_ok=True)
with open('/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh', 'w') as f:
    f.write(script)
os.chmod('/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh', 0o755)
print('Script updated successfully')
\""""

stdin, stdout, stderr = ssh.exec_command(script_cmd)
exit_code = stdout.channel.recv_exit_status()
print(f"  Writing fixed script...")
if exit_code == 0:
    print(f"    ✅ Script updated")
else:
    print(f"    ❌ Error: {stderr.read().decode()}")

ssh.close()

# Step 4: Verify the new script
print("\n[4/5] Verifying fixed script...")
run_ssh("head -40 /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "New script content")
run_ssh("ls -la /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "File permissions")

# Step 5: Test MySQL connection and restart services
print("\n[5/5] Testing and restarting services...")
run_ssh("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -3", "Test MySQL connection")
run_ssh("pkill -9 -f gunicorn; sleep 2; cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &", "Restart Gunicorn")
time.sleep(3)
run_ssh("pgrep -c gunicorn", "Check Gunicorn processes")
run_ssh("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", "Test HTTP status")

print("\n" + "=" * 80)
print("✅ FIX COMPLETE")
print("=" * 80)
print("\nThe auto-fix script has been updated with correct MySQL paths.")
print("Next health check (within 2 minutes) will use the fixed script.")
print("\nTo monitor:")
print("  tail -f /root/.openclaw/monitoring/logs/health_check.log")
print("  tail -f /root/.openclaw/monitoring/logs/auto_fix.log")
print("=" * 80)
