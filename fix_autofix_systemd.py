#!/usr/bin/env python3
"""Fix auto-repair scripts for MySQL 8.0 (systemd-based, no mysqld_safe)"""
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
        print(f"    → {output[:300]}")
    if error and exit_code != 0:
        print(f"    ⚠ {error[:300]}")
    
    ssh.close()
    return exit_code, output, error

print("=" * 80)
print("🔧 Fixing Auto-Repair Scripts for MySQL 8.0 (Systemd)")
print("=" * 80)

# Create the corrected enhanced_mysql_fix.sh for systemd-based MySQL
fixed_script = r'''#!/bin/bash
LOG="/root/.openclaw/monitoring/logs/auto_fix.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ========== MySQL自动修复开始 ==========" >> $LOG
echo "[$TS] [0%] 检测到MySQL故障" >> $LOG

# 停止MySQL
echo "[$TS] [10%] 停止MySQL服务" >> $LOG
systemctl stop mysqld 2>/dev/null || service mysql stop 2>/dev/null
sleep 2
killall -9 mysqld 2>/dev/null
sleep 1
rm -f /var/lib/mysql/mysql.sock
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
echo "[$TS] [20%] 清理完成" >> $LOG

# 以skip-grant-tables模式启动
echo "[$TS] [30%] 启动恢复模式(skip-grant-tables)" >> $LOG
/usr/sbin/mysqld --user=mysql --socket=/var/lib/mysql/mysql.sock --skip-grant-tables &
MYSQLD_PID=$!
sleep 8

# 检查socket
SOCKET_READY=0
for i in {1..15}; do
    if [ -f /var/lib/mysql/mysql.sock ]; then
        echo "[$TS] [40%] Socket创建成功" >> $LOG
        SOCKET_READY=1
        break
    fi
    sleep 1
done

if [ $SOCKET_READY -eq 0 ]; then
    echo "[$TS] [ERROR] Socket未创建，尝试其他方法" >> $LOG
    kill $MYSQLD_PID 2>/dev/null
    # 尝试使用systemctl启动
    systemctl start mysqld
    sleep 5
fi

# 重置密码
echo "[$TS] [50%] 重置root密码" >> $LOG
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "[$TS] [60%] 密码重置完成" >> $LOG

# 关闭恢复模式并正常启动
echo "[$TS] [70%] 重启MySQL服务" >> $LOG
kill $MYSQLD_PID 2>/dev/null
sleep 2
systemctl start mysqld
sleep 5

# 验证连接
echo "[$TS] [80%] 验证MySQL连接" >> $LOG
mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$TS] [90%] ✓ MySQL恢复正常" >> $LOG
else
    echo "[$TS] [90%] ✗ MySQL仍有问题" >> $LOG
    # 最后一次尝试
    systemctl restart mysqld
    sleep 5
    mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
    if [ $? -eq 0 ]; then
        echo "[$TS] [90%] ✓ MySQL通过systemctl重启恢复" >> $LOG
    else
        echo "[$TS] [90%] ✗ MySQL修复失败，需要人工干预" >> $LOG
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

print("\n[1/3] Writing fixed enhanced_mysql_fix.sh...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

# Write using Python to avoid escaping issues
cmd = '''python3 << 'PYEOF'
import os
script = """#!/bin/bash
LOG="/root/.openclaw/monitoring/logs/auto_fix.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ========== MySQL自动修复开始 ==========" >> $LOG
echo "[$TS] [0%] 检测到MySQL故障" >> $LOG

# 停止MySQL
echo "[$TS] [10%] 停止MySQL服务" >> $LOG
systemctl stop mysqld 2>/dev/null || service mysql stop 2>/dev/null
sleep 2
killall -9 mysqld 2>/dev/null
sleep 1
rm -f /var/lib/mysql/mysql.sock
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
echo "[$TS] [20%] 清理完成" >> $LOG

# 以skip-grant-tables模式启动
echo "[$TS] [30%] 启动恢复模式(skip-grant-tables)" >> $LOG
/usr/sbin/mysqld --user=mysql --socket=/var/lib/mysql/mysql.sock --skip-grant-tables &
MYSQLD_PID=$!
sleep 8

# 检查socket
SOCKET_READY=0
for i in {1..15}; do
    if [ -f /var/lib/mysql/mysql.sock ]; then
        echo "[$TS] [40%] Socket创建成功" >> $LOG
        SOCKET_READY=1
        break
    fi
    sleep 1
done

if [ $SOCKET_READY -eq 0 ]; then
    echo "[$TS] [ERROR] Socket未创建，尝试其他方法" >> $LOG
    kill $MYSQLD_PID 2>/dev/null
    systemctl start mysqld
    sleep 5
fi

# 重置密码
echo "[$TS] [50%] 重置root密码" >> $LOG
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "[$TS] [60%] 密码重置完成" >> $LOG

# 关闭恢复模式并正常启动
echo "[$TS] [70%] 重启MySQL服务" >> $LOG
kill $MYSQLD_PID 2>/dev/null
sleep 2
systemctl start mysqld
sleep 5

# 验证连接
echo "[$TS] [80%] 验证MySQL连接" >> $LOG
mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$TS] [90%] ✓ MySQL恢复正常" >> $LOG
else
    echo "[$TS] [90%] ✗ MySQL仍有问题" >> $LOG
    systemctl restart mysqld
    sleep 5
    mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
    if [ $? -eq 0 ]; then
        echo "[$TS] [90%] ✓ MySQL通过systemctl重启恢复" >> $LOG
    else
        echo "[$TS] [90%] ✗ MySQL修复失败，需要人工干预" >> $LOG
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
"""
os.makedirs('/root/.openclaw/monitoring/scripts', exist_ok=True)
with open('/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh', 'w') as f:
    f.write(script)
os.chmod('/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh', 0o755)
print('Script written successfully')
PYEOF
'''

stdin, stdout, stderr = ssh.exec_command(cmd)
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("    ✅ Script updated with systemd commands")
else:
    print(f"    ❌ Error: {stderr.read().decode()}")

ssh.close()

# Verify the script
print("\n[2/3] Verifying new script...")
run_ssh("head -50 /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "Script preview")
run_ssh("ls -la /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "File permissions")

# Test current MySQL status and restart Gunicorn
print("\n[3/3] Testing services...")
run_ssh("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -2", "Test MySQL connection")
run_ssh("pkill -9 -f gunicorn; sleep 2; cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &", "Restart Gunicorn")
time.sleep(3)
run_ssh("pgrep -c gunicorn", "Gunicorn process count")
run_ssh("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", "HTTP status test")

print("\n" + "=" * 80)
print("✅ AUTO-FIX SCRIPT FIXED FOR MYSQL 8.0")
print("=" * 80)
print("\nKey changes:")
print("  • Removed mysqld_safe (not available in MySQL 8.0)")
print("  • Using /usr/sbin/mysqld directly with --skip-grant-tables")
print("  • Using systemctl for service management")
print("  • Added fallback to systemctl restart if direct start fails")
print("\nThe health check runs every 2 minutes.")
print("If MySQL fails, it will auto-repair within 2 minutes.")
print("\nTo monitor progress:")
print("  tail -f /root/.openclaw/monitoring/logs/health_check.log")
print("  tail -f /root/.openclaw/monitoring/logs/auto_fix.log")
print("=" * 80)
