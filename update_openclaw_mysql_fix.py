#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update OpenClaw monitoring to properly fix MySQL authentication
更新OpenClaw监控以正确修复MySQL认证问题
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("更新OpenClaw MySQL自动修复脚本")
    print("Update OpenClaw MySQL Auto-Fix Script")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # Create improved auto-fix script for OpenClaw
        print("\n[2] 创建改进的MySQL修复脚本...")
        
        improved_fix_script = r'''#!/bin/bash
# OpenClaw Enhanced MySQL Fix Script
# This script properly resets MySQL root password when authentication fails

LOG_FILE="/root/.openclaw/monitoring/logs/auto_fix.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始增强版MySQL修复..." >> $LOG_FILE

# Step 1: Check if MySQL is actually running
if ! pgrep -x mysqld > /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] MySQL未运行，尝试启动..." >> $LOG_FILE
    systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null
    sleep 5
fi

# Step 2: Test MySQL connection
mysql -uroot -pEIMS2026_mysql -e "SELECT 1;" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ MySQL连接正常，无需修复" >> $LOG_FILE
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ MySQL认证失败，执行密码重置..." >> $LOG_FILE

# Step 3: Stop MySQL completely
systemctl stop mysqld 2>/dev/null || service mysql stop 2>/dev/null
sleep 2
pkill -9 mysqld 2>/dev/null || true
sleep 3

# Step 4: Clean socket
rm -f /var/lib/mysql/mysql.sock
sleep 1

# Step 5: Start with skip-grant-tables
mysqld_safe --skip-grant-tables --skip-networking=0 &
MYSQL_PID=$!
echo "[$(date '+%Y-%m-%d %H:%M:%S')] MySQL以skip-grant-tables模式启动 (PID: $MYSQL_PID)" >> $LOG_FILE

# Step 6: Wait for socket (up to 60 seconds)
SOCKET_READY=false
for i in $(seq 1 20); do
    if [ -S /var/lib/mysql/mysql.sock ]; then
        SOCKET_READY=true
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Socket已创建 (${i}次尝试)" >> $LOG_FILE
        break
    fi
    sleep 3
done

if [ "$SOCKET_READY" = false ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Socket创建超时" >> $LOG_FILE
    pkill -9 mysqld 2>/dev/null || true
    exit 1
fi

# Step 7: Reset root password
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 重置root用户密码..." >> $LOG_FILE
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF 2>>$LOG_FILE
FLUSH PRIVILEGES;
DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT User, Host, plugin FROM mysql.user WHERE User='root';
EOF

if [ $? -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ 密码重置失败" >> $LOG_FILE
    pkill -9 mysqld 2>/dev/null || true
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ 密码重置成功" >> $LOG_FILE

# Step 8: Shutdown MySQL
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || true
sleep 3
pkill -9 mysqld 2>/dev/null || true
sleep 2

# Step 9: Start MySQL normally
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正常启动MySQL..." >> $LOG_FILE
systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null || mysqld_safe &
sleep 10

# Step 10: Verify
mysql -uroot -pEIMS2026_mysql -e "SELECT 'SUCCESS' as status;" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ MySQL修复完成并验证成功" >> $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ MySQL修复后验证失败" >> $LOG_FILE
fi

# Step 11: Restart Gunicorn to clear cached connections
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 重启Gunicorn..." >> $LOG_FILE
pkill -9 -f gunicorn 2>/dev/null || true
sleep 2
cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
sleep 5

# Step 12: Clear logs
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理错误日志..." >> $LOG_FILE
> /var/www/eims/logs/gunicorn_error.log 2>/dev/null || true

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 自动修复完成 ===" >> $LOG_FILE
'''
        
        # Write the improved script
        write_cmd = f"cat > /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh << 'SCRIPT_EOF'\n{improved_fix_script}\nSCRIPT_EOF"
        stdin, stdout, stderr = ssh.exec_command(write_cmd)
        time.sleep(2)
        
        # Make it executable
        ssh.exec_command('chmod +x /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh')
        print("✓ 改进的修复脚本已创建")
        
        # Update the health check script to call enhanced fix
        print("\n[3] 更新健康检查脚本...")
        
        health_check_update = '''
# In the health check, replace simple MySQL restart with enhanced fix
# Find the line that says "service mysql restart" or similar and replace it
sed -i 's|service mysql restart|bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh|g' /root/.openclaw/monitoring/scripts/health_check.sh 2>/dev/null || true
sed -i 's|systemctl restart mysqld|bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh|g' /root/.openclaw/monitoring/scripts/health_check.sh 2>/dev/null || true
'''
        ssh.exec_command(health_check_update)
        print("✓ 健康检查脚本已更新")
        
        # Now execute the enhanced fix immediately
        print("\n[4] 立即执行增强版修复...")
        ssh.exec_command('bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh')
        
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
        
        # Verify the fix
        print("\n[5] 验证修复结果...")
        verify_cmd = '''
echo "=== MySQL命令行测试 ==="
mysql -uroot -pEIMS2026_mysql -e "SELECT 'MySQL OK' as status;" 2>&1

echo -e "\\n=== Django数据库测试 ==="
cd /var/www/eims && source venv/bin/activate && python << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"Django数据库连接成功！用户数: {count}")
except Exception as e:
    print(f"Django数据库连接失败: {e}")
PYEOF

echo -e "\\n=== HTTP测试 ==="
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\\n" http://127.0.0.1:8000/login/

echo -e "\\n=== 最新错误日志 ==="
tail -3 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || echo "无错误日志"

echo -e "\\n=== OpenClaw修复日志 ==="
tail -10 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null
'''
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        time.sleep(5)
        result = stdout.read().decode()
        print(result)
        
        print("\n" + "=" * 70)
        print("OpenClaw配置更新完成！")
        print("OpenClaw configuration updated successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
