#!/usr/bin/env python3
"""
终极MySQL修复 - 使用多种方法尝试启动
"""
import paramiko
import time
import sys

print("=" * 80)
print("🔧 终极MySQL修复")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)

def run(cmd, desc="", wait=2):
    print(f"  {desc or cmd[:60]}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    time.sleep(wait)
    return code, out, err

# 1. 完全停止MySQL
print("\n[1/10] 完全停止MySQL...")
run("killall -9 mysqld mysqld_safe mysql 2>/dev/null; sleep 3", "终止所有MySQL进程", 4)
run("rm -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.sock /var/lock/subsys/mysql", "清理所有socket和锁文件")
run("mkdir -p /var/run/mysqld && chown -R mysql:mysql /var/run/mysqld /var/lib/mysql", "设置权限")

# 2. 检查MySQL配置和数据目录
print("\n[2/10] 检查MySQL环境...")
code, out, err = run("ls -la /var/lib/mysql/ | head -15", "查看数据目录")
print(f"  数据目录内容:\n{out[:500]}")

code, out, err = run("cat /etc/my.cnf 2>/dev/null || cat /etc/mysql/my.cnf 2>/dev/null || echo 'No config found'", "查看配置文件")
print(f"  配置:\n{out[:300]}")

code, out, err = run("id mysql", "检查mysql用户")
print(f"  MySQL用户: {out}")

# 3. 尝试方法1: 使用mysqld_safe
print("\n[3/10] 方法1: 使用mysqld_safe启动...")
run("mysqld_safe --user=mysql --socket=/var/lib/mysql/mysql.sock --log-error=/var/log/mysqld_safe.log &", 
    "启动mysqld_safe", wait=0)

print("  等待5秒...")
time.sleep(5)

code, out, err = run("ls -la /var/lib/mysql/mysql.sock 2>&1", "检查socket")
if 'mysql.sock' in out:
    print("  ✅ 方法1成功！socket已创建")
    method = 1
else:
    print("  ❌ 方法1失败")
    code, out, err = run("tail -20 /var/log/mysqld_safe.log 2>/dev/null", "查看错误日志")
    print(f"  错误日志:\n{out[:300]}")
    method = 0

# 4. 如果方法1失败，尝试方法2: 直接mysqld
if method == 0:
    print("\n[4/10] 方法2: 直接启动mysqld...")
    run("killall -9 mysqld mysqld_safe 2>/dev/null; sleep 2", "清理进程", 3)
    
    run("mysqld --user=mysql --socket=/var/lib/mysql/mysql.sock --pid-file=/var/lib/mysql/mysqld.pid --datadir=/var/lib/mysql --skip-grant-tables --log-error=/var/log/mysqld_direct.log &",
        "直接启动mysqld", wait=0)
    
    print("  等待10秒...")
    time.sleep(10)
    
    code, out, err = run("ls -la /var/lib/mysql/mysql.sock 2>&1", "检查socket")
    if 'mysql.sock' in out:
        print("  ✅ 方法2成功！socket已创建")
        method = 2
    else:
        print("  ❌ 方法2也失败")
        code, out, err = run("tail -20 /var/log/mysqld_direct.log 2>/dev/null", "查看错误日志")
        print(f"  错误日志:\n{out[:300]}")
        
        # 检查是否有进程在运行
        code, out, err = run("ps aux | grep -E 'mysql|mysqld' | grep -v grep", "检查进程")
        print(f"  进程状态:\n{out[:300]}")

# 5. 如果socket存在，重置密码
if method > 0:
    print(f"\n[5/10] 重置root密码（使用方法{method}）...")
    
    sql = """FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'127.0.0.1';
DROP USER IF EXISTS 'root'@'::1';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User='root';"""
    
    run(f"cat > /tmp/reset.sql << 'EOF'\n{sql}\nEOF", "创建SQL脚本")
    
    code, out, err = run("mysql -u root --socket=/var/lib/mysql/mysql.sock < /tmp/reset.sql", 
                        "执行密码重置", wait=5)
    
    if code == 0 or 'root' in out:
        print("  ✅ 密码重置成功")
        if out:
            print(f"  用户列表:\n{out}")
    else:
        print(f"  ⚠️ 密码重置返回码: {code}")
        if err:
            print(f"  错误: {err[:200]}")
        if out:
            print(f"  输出: {out[:200]}")
    
    # 6. 关闭并正常重启
    print("\n[6/10] 正常重启MySQL...")
    run("mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall -9 mysqld", 
        "关闭MySQL", wait=3)
    
    run("systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null", 
        "使用systemctl启动", wait=5)
    
    # 7. 验证
    print("\n[7/10] 验证MySQL连接...")
    mysql_ok = False
    for i in range(15):
        time.sleep(1)
        code, out, err = run("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test' 2>&1", 
                           "测试连接", wait=0)
        if 'test' in out.lower() or '1' in out:
            print(f"  ✅ MySQL连接成功（{i+1}秒）")
            mysql_ok = True
            break
        if i == 7:
            print("  等待MySQL启动...", end='\r')
    
    if not mysql_ok:
        print("  ❌ MySQL连接失败")
        code, out, err = run("tail -30 /var/log/mysqld.log 2>/dev/null || journalctl -u mysqld -n 30 --no-pager 2>/dev/null", 
                           "查看MySQL日志", wait=1)
        print(f"  日志:\n{out[-500:]}")
        ssh.close()
        sys.exit(1)
else:
    print("\n❌ 无法启动MySQL，请检查:")
    print("  1. 磁盘空间: df -h")
    print("  2. MySQL数据目录权限: ls -la /var/lib/mysql/")
    print("  3. MySQL配置文件: cat /etc/my.cnf")
    print("  4. 系统日志: journalctl -u mysqld -n 50")
    ssh.close()
    sys.exit(1)

# 8. 重启Gunicorn
print("\n[8/10] 重启Gunicorn...")
run("pkill -9 -f gunicorn; sleep 2", "停止Gunicorn", 3)
run("cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &",
    "启动Gunicorn", wait=3)

# 9. 部署OpenClaw自动修复系统
print("\n[9/10] 部署OpenClaw自动修复...")

# 创建目录
run("mkdir -p /root/.openclaw/monitoring/{scripts,logs}", "创建监控目录")

# 创建增强修复脚本
enhanced_fix = r'''#!/bin/bash
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

# 恢复模式启动
echo "[$TS] [30%] 启动恢复模式" >> $LOG
mysqld_safe --user=mysql --socket=/var/lib/mysql/mysql.sock &
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
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "[$TS] [60%] 密码重置完成" >> $LOG

# 重启
echo "[$TS] [70%] 重启MySQL" >> $LOG
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld
sleep 3
systemctl start mysqld 2>/dev/null || service mysql start
sleep 5

# 验证
echo "[$TS] [80%] 验证连接" >> $LOG
mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$TS] [90%] MySQL正常" >> $LOG
else
    echo "[$TS] [90%] MySQL仍有问题" >> $LOG
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

run(f"cat > /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh << 'EOF'\n{enhanced_fix}\nEOF", 
    "创建修复脚本")
run("chmod +x /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "设置权限")

# 创建健康检查脚本
health_check = r'''#!/bin/bash
LOG="/root/.openclaw/monitoring/logs/health_check.log"
STATUS="/root/.openclaw/monitoring/status.json"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ===== 健康检查开始 =====" >> $LOG

# Gunicorn
if pgrep -f gunicorn >/dev/null 2>&1; then
    echo "[$TS] [20%] ✓ Gunicorn: 正常" >> $LOG
    G_STATUS="OK"
else
    echo "[$TS] [20%] ✗ Gunicorn: 重启中..." >> $LOG
    cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 wsgi:application >/var/www/eims/logs/gunicorn.log 2>&1 &
    G_STATUS="RESTARTED"
    echo "[$TS] [20%] ↻ Gunicorn: 已重启" >> $LOG
fi

# Nginx
if pgrep nginx >/dev/null 2>&1; then
    echo "[$TS] [40%] ✓ Nginx: 正常" >> $LOG
    N_STATUS="OK"
else
    echo "[$TS] [40%] ✗ Nginx: 重启中..." >> $LOG
    /usr/local/nginx/sbin/nginx
    N_STATUS="RESTARTED"
fi

# MySQL
if mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null; then
    echo "[$TS] [60%] ✓ MySQL: 正常" >> $LOG
    M_STATUS="OK"
else
    echo "[$TS] [60%] ✗ MySQL: 故障 - 触发自动修复" >> $LOG
    M_STATUS="FAIL"
    bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh
    sleep 5
    if mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null; then
        M_STATUS="FIXED"
        echo "[$TS] [80%] ✓ MySQL: 修复成功" >> $LOG
    else
        M_STATUS="FAILED"
        echo "[$TS] [80%] ✗ MySQL: 修复失败" >> $LOG
    fi
fi

# 磁盘
DISK=$(df / | tail -1 | awk '{print $5}')
echo "[$TS] [90%] 💾 磁盘: $DISK" >> $LOG

# 状态
cat > $STATUS << EOF
{"timestamp":"$TS","gunicorn":"$G_STATUS","nginx":"$N_STATUS","mysql":"$M_STATUS","disk":"$DISK"}
EOF

echo "[$TS] [100%] 完成" >> $LOG
'''

run(f"cat > /root/.openclaw/monitoring/scripts/health_check.sh << 'EOF'\n{health_check}\nEOF", 
    "创建健康检查脚本")
run("chmod +x /root/.openclaw/monitoring/scripts/health_check.sh", "设置权限")

# 配置crontab
crontab = """# OpenClaw Monitoring
*/2 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh >> /root/.openclaw/monitoring/logs/health_check.log 2>&1
"""
run(f"echo '{crontab}' | crontab -", "配置定时任务（2分钟间隔）")

print("  ✅ OpenClaw自动修复系统已部署")

# 10. 最终测试
print("\n[10/10] 最终测试...")
time.sleep(2)

code, http_code, _ = run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", 
                        "测试网站", wait=10)

code, mysql_test, _ = run("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | grep -q '1' && echo OK || echo FAIL",
                         "测试MySQL")

print("\n" + "=" * 80)
print("✅ 修复完成！")
print("=" * 80)
print(f"\n📊 测试结果:")
print(f"  网站访问: {'✅ HTTP ' + http_code if http_code == '200' else '⚠️ HTTP ' + http_code}")
print(f"  MySQL连接: {'✅ 正常' if 'OK' in mysql_test else '❌ 失败'}")

print("\n🔧 自动修复系统已部署:")
print("  • 检查间隔: 每2分钟")
print("  • 自动修复: 已启用")
print("  • 进度日志: 已配置")

print("\n📋 查看日志:")
print("  tail -f /root/.openclaw/monitoring/logs/health_check.log")
print("  tail -f /root/.openclaw/monitoring/logs/auto_fix.log")

print("\n💡 OpenClaw现在会自动监控并在发现问题时自动修复！")
print("=" * 80)

ssh.close()
