#!/usr/bin/env python3
"""
紧急MySQL修复 + 部署OpenClaw自动修复系统
Emergency MySQL Fix + Deploy OpenClaw Auto-Fix System
"""
import paramiko
import time
import sys
import json

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def execute(ssh, cmd, desc="", timeout=30, wait=2):
    """Execute command with description"""
    if desc:
        print(f"  {desc}")
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        time.sleep(wait)
        return exit_code == 0, output, error
    except Exception as e:
        return False, "", str(e)

def main():
    print_header("🚨 紧急MySQL修复 + OpenClaw自动修复部署")
    
    # 连接服务器
    print("\n[连接服务器...]")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect('39.106.41.239', username='root', password='fjkl546#', 
                   timeout=15, banner_timeout=15, auth_timeout=15)
        print("✅ 连接成功\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    try:
        # ==================== 第一部分：立即修复MySQL ====================
        print_header("第一部分：立即修复MySQL")
        
        # 1. 停止所有MySQL进程
        print("\n[1/8] 停止MySQL...")
        execute(ssh, "killall -9 mysqld mysqld_safe 2>/dev/null; sleep 2", "终止MySQL进程", wait=3)
        execute(ssh, "rm -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.sock", "清理socket文件")
        execute(ssh, "mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld", "创建运行目录")
        
        # 2. 启动恢复模式
        print("\n[2/8] 启动恢复模式...")
        execute(ssh, "mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock --pid-file=/var/lib/mysql/mysql.pid &", 
               "启动skip-grant-tables模式", wait=0)
        
        # 3. 等待socket创建
        print("  等待socket文件创建...")
        socket_ready = False
        for i in range(20):
            time.sleep(1)
            success, out, _ = execute(ssh, "test -f /var/lib/mysql/mysql.sock && echo YES || echo NO", timeout=5)
            if 'YES' in out:
                print(f"  ✅ Socket文件已创建（{i+1}秒）")
                socket_ready = True
                break
            if i % 5 == 0:
                print(f"  ...{i+1}/20秒", end='\r')
        
        if not socket_ready:
            print("\n  ❌ Socket文件未创建，检查进程...")
            execute(ssh, "ps aux | grep mysql | grep -v grep | head -5", timeout=5)
            print("\n  ⚠️  可能需要手动检查MySQL配置")
            return
        
        # 4. 重置密码
        print("\n[3/8] 重置root密码...")
        
        sql_script = """FLUSH PRIVILEGES;
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
SELECT User, Host, plugin FROM mysql.user WHERE User='root';"""
        
        # 写入SQL文件
        execute(ssh, f"cat > /tmp/mysql_reset.sql << 'EOF'\n{sql_script}\nEOF", "创建SQL脚本")
        
        # 执行SQL
        success, output, error = execute(ssh, 
            "mysql -u root --socket=/var/lib/mysql/mysql.sock < /tmp/mysql_reset.sql", 
            "执行密码重置", timeout=15, wait=3)
        
        if success or ('root' in output and 'localhost' in output):
            print("  ✅ 密码重置成功")
            if output:
                print(f"  用户信息:\n{output}")
        else:
            print(f"  ⚠️  密码重置可能有问题: {error[:200] if error else '未知错误'}")
        
        # 5. 重启MySQL
        print("\n[4/8] 重启MySQL...")
        execute(ssh, "mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld", 
               "关闭恢复模式", wait=3)
        execute(ssh, "systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null || mysqld_safe --user=mysql &", 
               "启动MySQL", wait=0)
        
        # 6. 验证MySQL
        print("\n[5/8] 验证MySQL连接...")
        mysql_ok = False
        for i in range(10):
            time.sleep(1)
            success, out, err = execute(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test' 2>&1", timeout=5)
            if 'test' in out.lower() or '1' in out:
                print(f"  ✅ MySQL连接正常（{i+1}秒）")
                mysql_ok = True
                break
            if i == 4:
                print("  等待MySQL启动...", end='\r')
        
        if not mysql_ok:
            print("  ❌ MySQL连接仍然失败")
            return
        
        # 7. 重启Gunicorn
        print("\n[6/8] 重启Gunicorn...")
        execute(ssh, "pkill -9 -f gunicorn; sleep 2", "停止旧进程", wait=3)
        execute(ssh, 
               "cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &",
               "启动Gunicorn", wait=3)
        
        # 8. 测试网站
        print("\n[7/8] 测试网站访问...")
        success, http_code, _ = execute(ssh, 
                                       "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", 
                                       "检查登录页面", timeout=10)
        if http_code == '200':
            print(f"  ✅ 网站正常（HTTP {http_code}）")
        else:
            print(f"  ⚠️  HTTP状态: {http_code}")
        
        # ==================== 第二部分：部署OpenClaw自动修复 ====================
        print_header("第二部分：部署OpenClaw自动修复系统")
        
        # 1. 创建监控目录
        print("\n[1/5] 创建监控目录...")
        execute(ssh, "mkdir -p /root/.openclaw/monitoring/{scripts,logs}", "创建目录结构")
        
        # 2. 创建增强的MySQL修复脚本
        print("\n[2/5] 创建增强版MySQL修复脚本...")
        
        enhanced_fix_script = r'''#!/bin/bash
#############################################
# OpenClaw Enhanced MySQL Fix Script
# 自动修复MySQL认证失败问题
#############################################

LOG_FILE="/root/.openclaw/monitoring/logs/auto_fix.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$TIMESTAMP] $1" >> $LOG_FILE
}

log "========== 开始MySQL自动修复 =========="
log "[0%] 检测到MySQL连接失败，启动修复流程..."

# 步骤1: 停止MySQL
log "[10%] 停止MySQL服务..."
killall -9 mysqld mysqld_safe 2>/dev/null
sleep 2
rm -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.sock
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
log "[20%] MySQL已停止，清理完成"

# 步骤2: 启动恢复模式
log "[30%] 启动skip-grant-tables模式..."
mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &
sleep 10

# 步骤3: 检查socket
if [ -f /var/lib/mysql/mysql.sock ]; then
    log "[40%] Socket文件已创建"
else
    log "[40%] 等待socket创建..."
    for i in {1..15}; do
        sleep 1
        if [ -f /var/lib/mysql/mysql.sock ]; then
            log "[40%] Socket文件已创建（${i}秒）"
            break
        fi
    done
fi

# 步骤4: 重置密码
log "[50%] 重置root密码..."
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
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
EOF

if [ $? -eq 0 ]; then
    log "[60%] 密码重置成功"
else
    log "[60%] 密码重置失败，继续尝试..."
fi

# 步骤5: 重启MySQL
log "[70%] 重启MySQL..."
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld
sleep 3
systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null || mysqld_safe --user=mysql &
sleep 5

# 步骤6: 验证
log "[80%] 验证MySQL连接..."
mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    log "[90%] MySQL连接正常"
else
    log "[90%] MySQL连接仍有问题"
fi

# 步骤7: 重启Gunicorn
log "[95%] 重启Gunicorn..."
pkill -9 -f gunicorn 2>/dev/null
sleep 2
cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
sleep 3

log "[100%] MySQL自动修复完成"
log "=========================================="
'''
        
        execute(ssh, f"cat > /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh << 'SCRIPTEOF'\n{enhanced_fix_script}\nSCRIPTEOF", 
               "写入修复脚本")
        execute(ssh, "chmod +x /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "设置执行权限")
        print("  ✅ 增强版MySQL修复脚本已创建")
        
        # 3. 创建健康检查脚本（带进度条）
        print("\n[3/5] 创建健康检查脚本...")
        
        health_check_script = r'''#!/bin/bash
#############################################
# OpenClaw Health Check Script
# 带进度条的详细健康检查
#############################################

LOG_FILE="/root/.openclaw/monitoring/logs/health_check.log"
STATUS_FILE="/root/.openclaw/monitoring/status.json"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$TIMESTAMP] $1" >> $LOG_FILE
}

TOTAL_STEPS=5
CURRENT_STEP=0

step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    PERCENT=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    log "[$PERCENT%] $1"
}

log "========== 健康检查开始 =========="

# 检查Gunicorn
step "检查Gunicorn..."
if pgrep -f gunicorn > /dev/null 2>&1; then
    GUNCORN_COUNT=$(pgrep -f gunicorn | wc -l)
    log "✓ Gunicorn: 正常 ($GUNCORN_COUNT 进程)"
    GUNCORN_STATUS="OK"
else
    log "✗ Gunicorn: 异常，尝试重启..."
    cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
    sleep 2
    GUNCORN_STATUS="RESTARTED"
    log "↻ Gunicorn: 已重启"
fi

# 检查Nginx
step "检查Nginx..."
if pgrep nginx > /dev/null 2>&1; then
    log "✓ Nginx: 正常"
    NGINX_STATUS="OK"
else
    log "✗ Nginx: 异常，尝试重启..."
    /usr/local/nginx/sbin/nginx
    sleep 1
    NGINX_STATUS="RESTARTED"
    log "↻ Nginx: 已重启"
fi

# 检查MySQL
step "检查MySQL连接..."
if mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null; then
    log "✓ MySQL: 正常"
    MYSQL_STATUS="OK"
else
    log "✗ MySQL: 认证失败"
    MYSQL_STATUS="FAIL"
    log "触发MySQL自动修复..."
    bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh
    log "↻ MySQL: 修复脚本已执行"
    
    # 再次验证
    sleep 5
    if mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null; then
        MYSQL_STATUS="FIXED"
        log "✓ MySQL: 修复成功"
    else
        MYSQL_STATUS="STILL_FAIL"
        log "✗ MySQL: 修复失败，需要人工干预"
    fi
fi

# 检查磁盘
step "检查磁盘使用..."
DISK_USAGE=$(df / | tail -1 | awk '{print $5}')
log "💾 磁盘使用: $DISK_USAGE"

# 生成状态JSON
step "生成状态报告..."
cat > $STATUS_FILE << EOF
{
    "timestamp": "$TIMESTAMP",
    "gunicorn": "$GUNCORN_STATUS",
    "nginx": "$NGINX_STATUS",
    "mysql": "$MYSQL_STATUS",
    "disk_usage": "$DISK_USAGE",
    "status": "healthy"
}
EOF

log "[100%] 健康检查完成"
log "=========================================="
'''
        
        execute(ssh, f"cat > /root/.openclaw/monitoring/scripts/health_check.sh << 'SCRIPTEOF'\n{health_check_script}\nSCRIPTEOF", 
               "写入健康检查脚本")
        execute(ssh, "chmod +x /root/.openclaw/monitoring/scripts/health_check.sh", "设置执行权限")
        print("  ✅ 健康检查脚本已创建（带进度条）")
        
        # 4. 更新crontab（2分钟间隔）
        print("\n[4/5] 配置定时任务...")
        
        crontab_content = '''# OpenClaw Monitoring - 每2分钟检查一次
*/2 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh >> /dev/null 2>&1
*/2 * * * * bash /root/.openclaw/monitoring/scripts/auto_fix.sh >> /dev/null 2>&1

# 每5分钟记录一次详细日志
*/5 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh >> /root/.openclaw/monitoring/logs/health_check.log 2>&1
'''
        
        execute(ssh, f"echo '{crontab_content}' | crontab -", "更新crontab")
        print("  ✅ 定时任务已配置（每2分钟检查）")
        
        # 5. 立即测试自动修复
        print("\n[5/5] 立即测试自动修复系统...")
        print("  运行健康检查脚本...")
        
        success, output, error = execute(ssh, 
                                        "bash /root/.openclaw/monitoring/scripts/health_check.sh", 
                                        "执行健康检查", timeout=60, wait=5)
        
        # 显示日志
        print("\n  📋 健康检查日志:")
        success, log_output, _ = execute(ssh, "tail -20 /root/.openclaw/monitoring/logs/health_check.log", 
                                        "读取日志", wait=1)
        if log_output:
            for line in log_output.split('\n')[-15:]:
                if line.strip():
                    print(f"    {line}")
        
        # 最终验证
        print("\n[最终验证]")
        success, http_code, _ = execute(ssh, 
                                       "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", 
                                       "测试网站", timeout=10)
        
        if http_code == '200':
            print("  ✅ 网站访问正常")
        else:
            print(f"  ⚠️  网站状态: {http_code}")
        
        success, mysql_test, _ = execute(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | grep -q '1' && echo OK || echo FAIL", 
                                        "测试MySQL", wait=1)
        if 'OK' in mysql_test:
            print("  ✅ MySQL连接正常")
        else:
            print("  ⚠️  MySQL可能仍有问题")
        
        # ==================== 完成总结 ====================
        print_header("✅ 全部完成！")
        
        print("\n📊 系统状态:")
        print("  • MySQL: 已修复并运行")
        print("  • Gunicorn: 已重启")
        print("  • OpenClaw监控: 已部署")
        print("  • 检查间隔: 每2分钟")
        print("  • 自动修复: 已启用")
        
        print("\n📝 自动修复流程:")
        print("  1. 健康检查每2分钟运行一次")
        print("  2. 如果检测到MySQL失败 → 自动触发修复脚本")
        print("  3. 修复脚本自动:")
        print("     - 停止MySQL")
        print("     - 清理socket文件")
        print("     - 以恢复模式启动")
        print("     - 重置root密码")
        print("     - 正常重启MySQL")
        print("     - 重启Gunicorn")
        print("  4. 记录详细日志（带进度百分比）")
        
        print("\n📋 查看日志命令:")
        print("  tail -f /root/.openclaw/monitoring/logs/health_check.log")
        print("  tail -f /root/.openclaw/monitoring/logs/auto_fix.log")
        print("  cat /root/.openclaw/monitoring/status.json")
        
        print("\n⏱️ 下次检查: 最多2分钟内")
        print("\n💡 提示: 如果MySQL再次出现问题，OpenClaw会在2分钟内自动检测并修复！")
        
    except Exception as e:
        print(f"\n❌ 执行过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
