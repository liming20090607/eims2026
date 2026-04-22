#!/usr/bin/env python3
"""
配置OpenClaw完整自动化监控系统
Configure OpenClaw Complete Automated Monitoring System
"""

import paramiko
import os
import time

print("=" * 80)
print("🤖 配置OpenClaw完整自动化系统")
print("Configure OpenClaw Complete Automation")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ 已连接服务器\n")
    
    # Step 1: Create OpenClaw monitoring directory structure
    print("[1/8] 创建OpenClaw监控目录...")
    dirs = [
        "/root/.openclaw/monitoring/scripts",
        "/root/.openclaw/monitoring/logs",
        "/root/.openclaw/monitoring/alerts"
    ]
    
    for dir_path in dirs:
        ssh.exec_command(f"mkdir -p {dir_path}", timeout=5)
    print("  ✅ 目录创建完成\n")
    
    # Step 2: Create comprehensive health check script
    print("[2/8] 创建健康检查脚本...")
    
    health_check_script = """#!/bin/bash
# OpenClaw Health Check Script
# Runs every 2 minutes to monitor system health

LOG="/root/.openclaw/monitoring/logs/health_check.log"
STATUS="/root/.openclaw/monitoring/status.json"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ===== 健康检查开始 =====" >> $LOG

# Check Gunicorn
if pgrep -f gunicorn >/dev/null 2>&1; then
    G_COUNT=$(pgrep -f gunicorn | wc -l)
    echo "[$TS] [20%] ✓ Gunicorn: 正常 ($G_COUNT 进程)" >> $LOG
    G_STATUS="OK"
else
    echo "[$TS] [20%] ✗ Gunicorn: 故障 - 重启中..." >> $LOG
    cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
    sleep 3
    if pgrep -f gunicorn >/dev/null 2>&1; then
        G_STATUS="RESTARTED"
        echo "[$TS] [20%] ↻ Gunicorn: 已重启" >> $LOG
    else
        G_STATUS="FAILED"
        echo "[$TS] [20%] ✗ Gunicorn: 重启失败" >> $LOG
    fi
fi

# Check Nginx
if pgrep nginx >/dev/null 2>&1; then
    echo "[$TS] [40%] ✓ Nginx: 正常" >> $LOG
    N_STATUS="OK"
else
    echo "[$TS] [40%] ✗ Nginx: 重启中..." >> $LOG
    /usr/local/nginx/sbin/nginx
    sleep 2
    if pgrep nginx >/dev/null 2>&1; then
        N_STATUS="RESTARTED"
        echo "[$TS] [40%] ↻ Nginx: 已重启" >> $LOG
    else
        N_STATUS="FAILED"
        echo "[$TS] [40%] ✗ Nginx: 重启失败" >> $LOG
    fi
fi

# Check MySQL
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

# Check disk usage
DISK=$(df / | tail -1 | awk '{print $5}')
echo "[$TS] [90%] 💾 磁盘: $DISK" >> $LOG

# Test HTTP
HTTP_CODE=$(curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/)
echo "[$TS] [95%] 🌐 HTTP: $HTTP_CODE" >> $LOG

# Generate status JSON
cat > $STATUS << EOF
{"timestamp":"$TS","gunicorn":"$G_STATUS","nginx":"$N_STATUS","mysql":"$M_STATUS","disk":"$DISK","http_code":"$HTTP_CODE"}
EOF

echo "[$TS] [100%] 检查完成" >> $LOG
echo "----------------------------------------" >> $LOG
"""
    
    # Write health check script
    write_cmd = f"""cat > /root/.openclaw/monitoring/scripts/health_check.sh << 'SCRIPTEOF'
{health_check_script}
SCRIPTEOF
chmod +x /root/.openclaw/monitoring/scripts/health_check.sh
echo "Health check script created"
"""
    stdin, stdout, stderr = ssh.exec_command(write_cmd, timeout=5)
    print(f"  {stdout.read().decode().strip()}\n")
    
    # Step 3: Create enhanced MySQL fix script
    print("[3/8] 创建MySQL自动修复脚本...")
    
    mysql_fix_script = """#!/bin/bash
# Enhanced MySQL Auto-Fix Script
LOG="/root/.openclaw/monitoring/logs/auto_fix.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ========== MySQL自动修复开始 ==========" >> $LOG
echo "[$TS] [0%] 检测到MySQL故障" >> $LOG

# Stop MySQL completely
echo "[$TS] [10%] 停止MySQL" >> $LOG
systemctl stop mysqld 2>/dev/null
killall -9 mysqld mysqld_safe 2>/dev/null
sleep 3
rm -f /var/lib/mysql/mysql.sock
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
echo "[$TS] [20%] 清理完成" >> $LOG

# Start in recovery mode
echo "[$TS] [30%] 启动恢复模式" >> $LOG
mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &
sleep 10

# Wait for socket
for i in {1..15}; do
    if [ -f /var/lib/mysql/mysql.sock ]; then
        echo "[$TS] [40%] Socket创建成功" >> $LOG
        break
    fi
    sleep 1
done

# Reset password
echo "[$TS] [50%] 重置密码" >> $LOG
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "[$TS] [60%] 密码重置完成" >> $LOG

# Restart normally
echo "[$TS] [70%] 重启MySQL" >> $LOG
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld
sleep 3
systemctl start mysqld 2>/dev/null || service mysql start
sleep 5

# Verify
echo "[$TS] [80%] 验证连接" >> $LOG
mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$TS] [90%] MySQL正常" >> $LOG
else
    echo "[$TS] [90%] MySQL仍有问题" >> $LOG
fi

# Restart Gunicorn
echo "[$TS] [95%] 重启Gunicorn" >> $LOG
pkill -9 -f gunicorn 2>/dev/null
sleep 2
cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &
sleep 3

echo "[$TS] [100%] 修复完成" >> $LOG
echo "[$TS] ============================" >> $LOG
"""
    
    write_mysql = f"""cat > /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh << 'SCRIPTEOF'
{mysql_fix_script}
SCRIPTEOF
chmod +x /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh
echo "MySQL fix script created"
"""
    stdin, stdout, stderr = ssh.exec_command(write_mysql, timeout=5)
    print(f"  {stdout.read().decode().strip()}\n")
    
    # Step 4: Create auto-deploy script
    print("[4/8] 创建自动部署脚本...")
    
    auto_deploy_script = f"""#!/bin/bash
# Auto-Deploy Script - Pull from Gitee and restart
LOG="/root/.openclaw/monitoring/logs/deploy.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ========== 自动部署开始 ==========" >> $LOG

cd {SERVER_PATH}

# Pull latest code
echo "[$TS] [10%] 拉取最新代码..." >> $LOG
git pull >> $LOG 2>&1

# Install dependencies
echo "[$TS] [30%] 安装依赖..." >> $LOG
source venv/bin/activate
pip install -r requirements.txt -q >> $LOG 2>&1

# Run migrations
echo "[$TS] [50%] 执行迁移..." >> $LOG
python manage.py migrate >> $LOG 2>&1

# Collect static files
echo "[$TS] [60%] 收集静态文件..." >> $LOG
python manage.py collectstatic --noinput >> $LOG 2>&1

# Restart Gunicorn
echo "[$TS] [70%] 重启Gunicorn..." >> $LOG
pkill -9 -f gunicorn 2>/dev/null
sleep 2
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
sleep 5

# Verify
echo "[$TS] [80%] 验证服务..." >> $LOG
HTTP_CODE=$(curl -o /dev/null -s -w '%{{http_code}}' http://127.0.0.1:8000/login/)
echo "[$TS] [90%] HTTP状态: $HTTP_CODE" >> $LOG

if [ "$HTTP_CODE" == "200" ]; then
    echo "[$TS] [100%] 部署成功" >> $LOG
else
    echo "[$TS] [100%] 部署可能有问题 (HTTP $HTTP_CODE)" >> $LOG
fi

echo "[$TS] ============================" >> $LOG
"""
    
    write_deploy = f"""cat > /root/.openclaw/monitoring/scripts/auto_deploy.sh << 'SCRIPTEOF'
{auto_deploy_script}
SCRIPTEOF
chmod +x /root/.openclaw/monitoring/scripts/auto_deploy.sh
echo "Auto-deploy script created"
"""
    stdin, stdout, stderr = ssh.exec_command(write_deploy, timeout=5)
    print(f"  {stdout.read().decode().strip()}\n")
    
    # Step 5: Configure crontab for automated tasks
    print("[5/8] 配置定时任务...")
    
    crontab_config = """# OpenClaw Automated Monitoring
# Health check every 2 minutes
*/2 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh >> /root/.openclaw/monitoring/logs/health_check.log 2>&1

# Auto-deploy every hour (optional, can be triggered manually)
# 0 * * * * bash /root/.openclaw/monitoring/scripts/auto_deploy.sh >> /root/.openclaw/monitoring/logs/deploy.log 2>&1

# Daily log cleanup at 2 AM
0 2 * * * find /root/.openclaw/monitoring/logs -name "*.log" -mtime +7 -delete
"""
    
    write_cron = f"""echo '{crontab_config}' | crontab -
crontab -l | grep -c openclaw
"""
    stdin, stdout, stderr = ssh.exec_command(write_cron, timeout=5)
    count = stdout.read().decode().strip()
    print(f"  ✅ 已配置 {count} 个定时任务\n")
    
    # Step 6: Create status dashboard API
    print("[6/8] 创建状态API...")
    
    api_view = """from django.http import JsonResponse
import json
import os

def openclaw_status(request):
    status_file = '/root/.openclaw/monitoring/status.json'
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        return JsonResponse(status)
    except:
        return JsonResponse({'error': 'Status not available'}, status=500)

def openclaw_trigger_fix(request):
    import subprocess
    try:
        subprocess.Popen(['bash', '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'])
        return JsonResponse({'message': 'Fix triggered'})
    except:
        return JsonResponse({'error': 'Failed to trigger fix'}, status=500)
"""
    
    # Add to urls.py
    add_urls = f"""
# Add OpenClaw API routes
grep -q "openclaw_status" {SERVER_PATH}/urls.py || sed -i '/^urlpatterns/a\\    path(\"openclaw/api/status/\", views.openclaw_status),\\n    path(\"openclaw/api/trigger-fix/\", views.openclaw_trigger_fix),' {SERVER_PATH}/urls.py

# Add views
grep -q "def openclaw_status" {SERVER_PATH}/views_index.py || cat >> {SERVER_PATH}/views_index.py << 'PYEOF'

{api_view}
PYEOF

echo "API endpoints added"
"""
    stdin, stdout, stderr = ssh.exec_command(add_urls, timeout=5)
    print(f"  {stdout.read().decode().strip()}\n")
    
    # Step 7: Initialize log files
    print("[7/8] 初始化日志文件...")
    log_files = [
        "/root/.openclaw/monitoring/logs/health_check.log",
        "/root/.openclaw/monitoring/logs/auto_fix.log",
        "/root/.openclaw/monitoring/logs/deploy.log"
    ]
    
    for log_file in log_files:
        ssh.exec_command(f"touch {log_file}", timeout=5)
    
    # Create initial status
    init_status = '{"timestamp":"initial","gunicorn":"unknown","nginx":"unknown","mysql":"unknown","disk":"unknown","http_code":"unknown"}'
    ssh.exec_command(f"echo '{init_status}' > /root/.openclaw/monitoring/status.json", timeout=5)
    print("  ✅ 日志文件已初始化\n")
    
    # Step 8: Run initial health check
    print("[8/8] 执行初始健康检查...")
    ssh.exec_command("bash /root/.openclaw/monitoring/scripts/health_check.sh", timeout=30)
    time.sleep(5)
    
    # Read status
    stdin, stdout, stderr = ssh.exec_command("cat /root/.openclaw/monitoring/status.json")
    status = stdout.read().decode().strip()
    print(f"  当前状态: {status}\n")
    
    # Final summary
    print("=" * 80)
    print("✅ OpenClaw自动化系统配置完成！")
    print("=" * 80)
    print("\n📊 系统组件:")
    print("  • 健康检查: 每2分钟自动运行")
    print("  • MySQL修复: 自动检测并修复")
    print("  • Gunicorn: 自动重启")
    print("  • Nginx: 自动重启")
    print("  • 日志管理: 自动清理7天前的日志")
    print("\n📁 文件位置:")
    print("  • 脚本: /root/.openclaw/monitoring/scripts/")
    print("  • 日志: /root/.openclaw/monitoring/logs/")
    print("  • 状态: /root/.openclaw/monitoring/status.json")
    print("\n🔧 管理命令:")
    print("  • 查看状态: cat /root/.openclaw/monitoring/status.json")
    print("  • 查看日志: tail -f /root/.openclaw/monitoring/logs/health_check.log")
    print("  • 手动修复: bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh")
    print("  • 手动部署: bash /root/.openclaw/monitoring/scripts/auto_deploy.sh")
    print("\n🌐 API端点:")
    print("  • 状态查询: http://39.106.41.239/openclaw/api/status/")
    print("  • 触发修复: http://39.106.41.239/openclaw/api/trigger-fix/")
    print("\n⏰ 配置时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80)
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 配置失败: {str(e)}")
    import traceback
    traceback.print_exc()
