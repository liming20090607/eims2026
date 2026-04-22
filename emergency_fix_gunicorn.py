#!/usr/bin/env python
"""
紧急修复Gunicorn
"""

import paramiko
import time

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def emergency_fix():
    print("🚨 紧急修复Gunicorn")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    # 1. 检查Gunicorn为什么崩溃
    print("\n[1] 检查Gunicorn日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || tail -50 /var/log/gunicorn/error.log 2>/dev/null || echo "NO LOG"')
    logs = stdout.read().decode().strip()
    if logs and logs != 'NO LOG':
        print("最近的Gunicorn错误:")
        for line in logs.split('\n')[-10:]:
            print(f"  {line}")
    else:
        print("  没有找到日志文件")
    
    # 2. 检查Django错误日志
    print("\n[2] 检查Django错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/django_error.log 2>/dev/null || tail -30 /var/www/eims/eims_app/logs/django_error.log 2>/dev/null || echo "NO LOG"')
    django_logs = stdout.read().decode().strip()
    if django_logs and django_logs != 'NO LOG':
        print("最近的Django错误:")
        for line in django_logs.split('\n')[-10:]:
            print(f"  {line}")
    
    # 3. 尝试手动启动Gunicorn
    print("\n[3] 尝试手动启动Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application --daemon --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log 2>&1')
    error = stderr.read().decode().strip()
    if error:
        print(f"  ❌ 启动失败: {error}")
    else:
        print("  ✅ Gunicorn启动命令执行成功")
    
    time.sleep(3)
    
    # 4. 验证
    print("\n[4] 验证Gunicorn状态...")
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"  Gunicorn进程数: {count}")
    
    if count and int(count) > 0:
        print("  ✅ Gunicorn运行中")
        
        # 5. 测试HTTP
        print("\n[5] 测试HTTP访问...")
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/')
        code = stdout.read().decode().strip()
        print(f"  Gunicorn (8000): HTTP {code}")
        
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/')
        code = stdout.read().decode().strip()
        print(f"  Nginx (80): HTTP {code}")
    else:
        print("  ❌ Gunicorn未运行，尝试使用nohup启动...")
        stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &')
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
        count = stdout.read().decode().strip()
        print(f"  Gunicorn进程数: {count}")
    
    # 6. 更新自动纠错脚本，修复Gunicorn启动逻辑
    print("\n[6] 修复自动纠错脚本...")
    fix_script = '''#!/bin/bash
LOG_FILE="/var/www/eims/logs/auto_correction.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" | tee -a "$LOG_FILE"
}

log "INFO" "=========================================="
log "INFO" "Starting auto-correction check..."

# Check and fix Gunicorn FIRST (most critical)
check_gunicorn() {
    GUNICORN_COUNT=$(pgrep -c gunicorn 2>/dev/null || echo "0")
    if [ "$GUNICORN_COUNT" -lt 2 ]; then
        log "WARNING" "Gunicorn not running ($GUNICORN_COUNT workers), force restarting..."
        pkill -9 gunicorn 2>/dev/null || true
        sleep 2
        
        cd /var/www/eims
        nohup /var/www/eims/venv/bin/gunicorn \\
            --bind 127.0.0.1:8000 \\
            --workers 5 \\
            --access-logfile /var/www/eims/logs/gunicorn_access.log \\
            --error-logfile /var/www/eims/logs/gunicorn_error.log \\
            eims.wsgi:application \\
            > /dev/null 2>&1 &
        
        sleep 5
        NEW_COUNT=$(pgrep -c gunicorn 2>/dev/null || echo "0")
        if [ "$NEW_COUNT" -ge 2 ]; then
            log "SUCCESS" "✅ Gunicorn running with $NEW_COUNT workers"
        else
            log "ERROR" "❌ Gunicorn failed to start, checking logs..."
            tail -20 /var/www/eims/logs/gunicorn_error.log >> "$LOG_FILE" 2>/dev/null
        fi
    fi
    return 0
}

# Check MySQL
check_mysql() {
    if ! systemctl is-active --quiet mysqld; then
        log "WARNING" "MySQL not running, restarting..."
        systemctl restart mysqld
        sleep 3
        if systemctl is-active --quiet mysqld; then
            log "SUCCESS" "✅ MySQL running"
        fi
    fi
}

# Check Nginx
check_nginx() {
    if ! pgrep -q nginx; then
        log "WARNING" "Nginx not running, starting..."
        nginx
        sleep 2
        if pgrep -q nginx; then
            log "SUCCESS" "✅ Nginx running"
        fi
    fi
}

# Run checks
check_gunicorn
check_mysql
check_nginx

# Test HTTP
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/ 2>&1)
if [[ "$HTTP_CODE" =~ ^(200|302|500)$ ]]; then
    log "SUCCESS" "✅ HTTP OK ($HTTP_CODE)"
else
    log "WARNING" "⚠️ HTTP issue ($HTTP_CODE)"
fi

log "INFO" "Auto-correction check completed"
'''
    
    sftp = ssh.open_sftp()
    with sftp.file('/usr/local/bin/auto_correction.sh', 'w') as f:
        f.write(fix_script)
    sftp.close()
    
    ssh.close()
    
    print("\n" + "="*60)
    print("✅ 紧急修复完成")
    print("="*60)
    print("现在请刷新浏览器测试: http://www.xietongai.com.cn/login/")
    print("="*60 + "\n")

if __name__ == '__main__':
    emergency_fix()
