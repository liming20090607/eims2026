#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cooperative fix with OpenClaw for MySQL authentication issue
与OpenClaw协作修复MySQL认证问题
"""
import paramiko
import time
import json

def main():
    print("=" * 70)
    print("OpenClaw协作修复MySQL认证问题")
    print("Cooperative MySQL Authentication Fix with OpenClaw")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # Step 1: Check OpenClaw monitoring logs
        print("\n[2] 检查OpenClaw监控日志...")
        stdin, stdout, stderr = ssh.exec_command('tail -30 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null || echo "No log"')
        health_log = stdout.read().decode()
        print(health_log[:500])
        
        # Step 2: Check OpenClaw auto-fix attempts
        print("\n[3] 检查OpenClaw自动修复记录...")
        stdin, stdout, stderr = ssh.exec_command('tail -20 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null || echo "No log"')
        autofix_log = stdout.read().decode()
        print(autofix_log[:500])
        
        # Step 3: Current service status
        print("\n[4] 当前服务状态...")
        status_cmd = '''
echo "=== Gunicorn ==="
ps aux | grep gunicorn | grep -v grep | wc -l

echo -e "\\n=== Nginx ==="
ps aux | grep nginx | grep -v grep | wc -l

echo -e "\\n=== MySQL ==="
systemctl is-active mysqld 2>/dev/null || service mysql status 2>/dev/null || echo "Unknown"

echo -e "\\n=== Port 8000 ==="
netstat -tlnp | grep :8000 || ss -tlnp | grep :8000 || echo "Not listening"

echo -e "\\n=== Port 80 ==="
netstat -tlnp | grep :80 || ss -tlnp | grep :80 || echo "Not listening"
'''
        stdin, stdout, stderr = ssh.exec_command(status_cmd)
        status_output = stdout.read().decode()
        print(status_output)
        
        # Step 4: Test MySQL connection
        print("\n[5] 测试MySQL连接...")
        test_mysql = '''
echo "Command line test:"
mysql -uroot -pEIMS2026_mysql -e "SELECT 'OK' as status;" 2>&1

echo -e "\\nSocket file:"
ls -la /var/lib/mysql/mysql.sock 2>/dev/null || echo "Socket not found"

echo -e "\\nMySQL process:"
ps aux | grep mysqld | grep -v grep | head -2
'''
        stdin, stdout, stderr = ssh.exec_command(test_mysql)
        mysql_test = stdout.read().decode()
        print(mysql_test)
        
        # Step 5: Check error logs
        print("\n[6] 检查错误日志...")
        stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null | grep -i "access denied" || echo "No recent errors"')
        error_log = stdout.read().decode()
        print(error_log)
        
        # Step 6: Execute comprehensive fix
        print("\n[7] 执行综合修复...")
        
        fix_script = r'''#!/bin/bash
set -e

echo "[步骤 1] 停止所有相关服务..."
pkill -9 -f gunicorn || true
sleep 2
fuser -k 8000/tcp 2>/dev/null || true
sleep 2

echo "[步骤 2] 完全停止MySQL..."
systemctl stop mysqld 2>/dev/null || service mysql stop 2>/dev/null || true
sleep 3
pkill -9 mysqld || true
sleep 2

echo "[步骤 3] 清理socket文件..."
rm -f /var/lib/mysql/mysql.sock
rm -f /tmp/mysql.sock
sleep 1

echo "[步骤 4] 以skip-grant-tables模式启动MySQL..."
mysqld_safe --skip-grant-tables --skip-networking=0 &
MYSQL_PID=$!
echo "MySQL PID: $MYSQL_PID"

echo "[步骤 5] 等待socket创建（最多60秒）..."
for i in $(seq 1 20); do
    if [ -S /var/lib/mysql/mysql.sock ]; then
        echo "✓ Socket已创建（${i}次尝试）"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "✗ Socket创建超时"
        exit 1
    fi
    sleep 3
done

echo "[步骤 6] 重置root用户密码..."
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;

-- 删除所有root用户
DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;

-- 重新创建root用户
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- 授予权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

FLUSH PRIVILEGES;

-- 验证
SELECT User, Host, plugin FROM mysql.user WHERE User='root';
EOF

echo "[步骤 7] 关闭MySQL..."
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown || true
sleep 5
pkill -9 mysqld || true
sleep 3

echo "[步骤 8] 正常启动MySQL..."
systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null || mysqld_safe &
sleep 10

echo "[步骤 9] 验证MySQL连接..."
mysql -uroot -pEIMS2026_mysql -e "SELECT 'SUCCESS' as status;" 2>&1

echo "[步骤 10] 启动Gunicorn..."
cd /var/www/eims
source venv/bin/activate
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
sleep 5

echo "[步骤 11] 重启Nginx..."
/usr/local/nginx/sbin/nginx -s reload 2>/dev/null || /usr/local/nginx/sbin/nginx

echo "[步骤 12] 最终验证..."
sleep 3
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/
echo ""

echo "=== 修复完成 ==="
'''
        
        # Write script to server
        stdin, stdout, stderr = ssh.exec_command('cat > /tmp/cooperative_fix.sh << \'SCRIPT_EOF\'\n' + fix_script + '\nSCRIPT_EOF')
        time.sleep(2)
        
        # Make executable and run
        print("\n[8] 执行修复脚本...")
        stdin, stdout, stderr = ssh.exec_command('chmod +x /tmp/cooperative_fix.sh && bash /tmp/cooperative_fix.sh')
        
        # Wait for completion (this takes time)
        print("修复脚本正在执行，请稍候...")
        for i in range(60):
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep cooperative_fix | grep -v grep | wc -l')
            running = int(stdout.read().decode().strip())
            if running == 0:
                print(f"✓ 修复脚本已完成（{i*2}秒）")
                break
            if i % 10 == 0:
                print(f"  修复进行中... ({i*2}秒)")
        
        # Get results
        print("\n[9] 获取修复结果...")
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/fix_result.txt 2>/dev/null || echo "No result file"')
        result = stdout.read().decode()
        print(result[:1000])
        
        # Step 10: Final verification
        print("\n[10] 最终验证...")
        verify_cmd = '''
echo "=== Gunicorn ==="
ps aux | grep gunicorn | grep -v grep | wc -l

echo -e "\\n=== Nginx ==="
ps aux | grep nginx | grep -v grep | wc -l

echo -e "\\n=== MySQL ==="
mysql -uroot -pEIMS2026_mysql -e "SELECT 'MySQL OK' as status;" 2>&1

echo -e "\\n=== HTTP Test ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\\n" http://127.0.0.1:8000/login/

echo -e "\\n=== Recent Errors ==="
tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null | grep -i "error\|denied" || echo "No errors"
'''
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        final_status = stdout.read().decode()
        print(final_status)
        
        print("\n" + "=" * 70)
        print("修复完成！请检查以上输出确认系统状态")
        print("Fix completed! Please check the output above to confirm system status")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
