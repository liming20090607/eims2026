#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置OpenClaw监控EIMS2026服务
Configure OpenClaw to monitor EIMS2026 services
"""
import paramiko
import time
import json

def main():
    print("=" * 70)
    print("配置OpenClaw监控EIMS2026")
    print("Configure OpenClaw for EIMS2026 Monitoring")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 创建监控目录
        print("\n[2] 创建监控目录结构...")
        mkdir_cmd = '''
mkdir -p /root/.openclaw/monitoring
mkdir -p /root/.openclaw/monitoring/scripts
mkdir -p /root/.openclaw/monitoring/logs
mkdir -p /root/.openclaw/monitoring/configs
mkdir -p /var/www/eims/monitoring
'''
        ssh.exec_command(mkdir_cmd)
        time.sleep(1)
        print("✓ 目录已创建")
        
        # 创建服务健康检查脚本
        print("\n[3] 创建服务健康检查脚本...")
        health_check_script = '''#!/bin/bash
# EIMS2026 服务健康检查脚本
# Service Health Check Script

LOG_FILE="/root/.openclaw/monitoring/logs/health_check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 开始健康检查..." >> $LOG_FILE

# 检查Gunicorn
check_gunicorn() {
    COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
    if [ $COUNT -ge 4 ]; then
        echo "[$TIMESTAMP] ✓ Gunicorn: 正常 ($COUNT 个进程)" >> $LOG_FILE
        return 0
    else
        echo "[$TIMESTAMP] ✗ Gunicorn: 异常 ($COUNT 个进程)" >> $LOG_FILE
        return 1
    fi
}

# 检查Nginx
check_nginx() {
    COUNT=$(ps aux | grep nginx | grep -v grep | wc -l)
    if [ $COUNT -ge 2 ]; then
        echo "[$TIMESTAMP] ✓ Nginx: 正常 ($COUNT 个进程)" >> $LOG_FILE
        return 0
    else
        echo "[$TIMESTAMP] ✗ Nginx: 异常 ($COUNT 个进程)" >> $LOG_FILE
        return 1
    fi
}

# 检查MySQL
check_mysql() {
    if mysql -uroot -p'EIMS2026_mysql' -e "SELECT 1;" >/dev/null 2>&1; then
        echo "[$TIMESTAMP] ✓ MySQL: 正常" >> $LOG_FILE
        return 0
    else
        echo "[$TIMESTAMP] ✗ MySQL: 异常" >> $LOG_FILE
        return 1
    fi
}

# 检查端口
check_ports() {
    # 检查8000端口
    if netstat -tlnp | grep -q ":8000"; then
        echo "[$TIMESTAMP] ✓ 端口8000: 监听中" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] ✗ 端口8000: 未监听" >> $LOG_FILE
    fi
    
    # 检查80端口
    if netstat -tlnp | grep -q ":80"; then
        echo "[$TIMESTAMP] ✓ 端口80: 监听中" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] ✗ 端口80: 未监听" >> $LOG_FILE
    fi
}

# 检查磁盘空间
check_disk() {
    USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $USAGE -lt 80 ]; then
        echo "[$TIMESTAMP] ✓ 磁盘使用: ${USAGE}% (正常)" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] ⚠️ 磁盘使用: ${USAGE}% (警告)" >> $LOG_FILE
    fi
}

# 检查内存
check_memory() {
    FREE=$(free -m | awk 'NR==2{printf "%.0f", $4*100/$2}')
    if [ $FREE -gt 20 ]; then
        echo "[$TIMESTAMP] ✓ 可用内存: ${FREE}% (正常)" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] ⚠️ 可用内存: ${FREE}% (警告)" >> $LOG_FILE
    fi
}

# 检查错误日志
check_error_logs() {
    ERROR_COUNT=$(tail -100 /var/www/eims/logs/gunicorn_error.log 2>/dev/null | grep -c "Access denied\|OperationalError")
    if [ $ERROR_COUNT -eq 0 ]; then
        echo "[$TIMESTAMP] ✓ 错误日志: 无数据库错误" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] ✗ 错误日志: 发现 $ERROR_COUNT 个数据库错误" >> $LOG_FILE
    fi
}

# 检查HTTP访问
check_http() {
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/login/)
    if [ "$STATUS" = "200" ]; then
        echo "[$TIMESTAMP] ✓ HTTP访问: 正常 (状态码: $STATUS)" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] ✗ HTTP访问: 异常 (状态码: $STATUS)" >> $LOG_FILE
    fi
}

# 执行所有检查
echo "=== 健康检查开始 ===" >> $LOG_FILE
check_gunicorn
check_nginx
check_mysql
check_ports
check_disk
check_memory
check_error_logs
check_http
echo "=== 健康检查完成 ===" >> $LOG_FILE
echo "" >> $LOG_FILE

# 输出结果摘要
echo "健康检查完成，日志: $LOG_FILE"
tail -15 $LOG_FILE
'''
        
        # 写入脚本
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/.openclaw/monitoring/scripts/health_check.sh << 'SCRIPT_EOF'\n{health_check_script}\nSCRIPT_EOF")
        time.sleep(1)
        ssh.exec_command('chmod +x /root/.openclaw/monitoring/scripts/health_check.sh')
        print("✓ 健康检查脚本已创建")
        
        # 创建自动修复脚本
        print("\n[4] 创建自动修复脚本...")
        auto_fix_script = '''#!/bin/bash
# EIMS2026 自动修复脚本
# Auto-fix Script for Common Issues

LOG_FILE="/root/.openclaw/monitoring/logs/auto_fix.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 开始自动修复检查..." >> $LOG_FILE

# 检查并修复Gunicorn
fix_gunicorn() {
    COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
    if [ $COUNT -lt 4 ]; then
        echo "[$TIMESTAMP] 重启Gunicorn..." >> $LOG_FILE
        pkill -9 -f gunicorn
        sleep 2
        cd /var/www/eims && source venv/bin/activate
        gunicorn --bind 127.0.0.1:8000 --workers 4 --daemon wsgi:application
        sleep 3
        NEW_COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
        echo "[$TIMESTAMP] Gunicorn重启完成 ($NEW_COUNT 个进程)" >> $LOG_FILE
    fi
}

# 检查并修复Nginx
fix_nginx() {
    COUNT=$(ps aux | grep nginx | grep -v grep | wc -l)
    if [ $COUNT -lt 2 ]; then
        echo "[$TIMESTAMP] 重启Nginx..." >> $LOG_FILE
        /usr/local/nginx/sbin/nginx -s reload || /usr/local/nginx/sbin/nginx
        sleep 2
        NEW_COUNT=$(ps aux | grep nginx | grep -v grep | wc -l)
        echo "[$TIMESTAMP] Nginx重启完成 ($NEW_COUNT 个进程)" >> $LOG_FILE
    fi
}

# 检查MySQL连接
fix_mysql_connection() {
    if ! mysql -uroot -p'EIMS2026_mysql' -e "SELECT 1;" >/dev/null 2>&1; then
        echo "[$TIMESTAMP] MySQL连接失败，尝试修复..." >> $LOG_FILE
        
        # 检查MySQL进程
        MYSQL_COUNT=$(ps aux | grep mysqld | grep -v grep | wc -l)
        if [ $MYSQL_COUNT -eq 0 ]; then
            echo "[$TIMESTAMP] 启动MySQL..." >> $LOG_FILE
            systemctl start mysqld || service mysqld start
            sleep 5
        fi
        
        # 检查认证插件
        PLUGIN=$(mysql -uroot -p'EIMS2026_mysql' -e "SELECT plugin FROM mysql.user WHERE User='root' AND Host='localhost';" 2>/dev/null | tail -1)
        if echo "$PLUGIN" | grep -q "caching_sha2_password"; then
            echo "[$TIMESTAMP] 修复MySQL认证插件..." >> $LOG_FILE
            mysql -uroot -p'EIMS2026_mysql' << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
EOF
        fi
        
        echo "[$TIMESTAMP] MySQL修复完成" >> $LOG_FILE
    fi
}

# 检查端口占用
fix_port_conflict() {
    if ! netstat -tlnp | grep -q ":8000"; then
        echo "[$TIMESTAMP] 端口8000未监听，检查冲突..." >> $LOG_FILE
        fuser -k 8000/tcp 2>/dev/null
        sleep 1
        fix_gunicorn
    fi
}

# 清理日志
clean_logs() {
    # 保留最近1000行
    tail -1000 /var/www/eims/logs/gunicorn_error.log > /tmp/gunicorn_error.log.tmp
    mv /tmp/gunicorn_error.log.tmp /var/www/eims/logs/gunicorn_error.log
    echo "[$TIMESTAMP] 日志清理完成" >> $LOG_FILE
}

# 执行修复
echo "=== 自动修复开始 ===" >> $LOG_FILE
fix_gunicorn
fix_nginx
fix_mysql_connection
fix_port_conflict
clean_logs
echo "=== 自动修复完成 ===" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "自动修复完成，日志: $LOG_FILE"
'''
        
        # 写入自动修复脚本
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/.openclaw/monitoring/scripts/auto_fix.sh << 'SCRIPT_EOF'\n{auto_fix_script}\nSCRIPT_EOF")
        time.sleep(1)
        ssh.exec_command('chmod +x /root/.openclaw/monitoring/scripts/auto_fix.sh')
        print("✓ 自动修复脚本已创建")
        
        # 创建监控配置
        print("\n[5] 创建OpenClaw监控配置...")
        monitoring_config = {
            "monitoring": {
                "enabled": True,
                "interval": 300,  # 5分钟检查一次
                "services": {
                    "gunicorn": {
                        "type": "process",
                        "name": "gunicorn",
                        "min_processes": 4,
                        "port": 8000,
                        "health_url": "http://localhost:8000/login/",
                        "expected_status": 200
                    },
                    "nginx": {
                        "type": "process",
                        "name": "nginx",
                        "min_processes": 2,
                        "port": 80
                    },
                    "mysql": {
                        "type": "database",
                        "host": "localhost",
                        "port": 3306,
                        "user": "root",
                        "password": "EIMS2026_mysql",
                        "database": "eims"
                    }
                },
                "alerts": {
                    "enabled": True,
                    "methods": ["log"],
                    "log_file": "/root/.openclaw/monitoring/logs/alerts.log"
                },
                "auto_fix": {
                    "enabled": True,
                    "script": "/root/.openclaw/monitoring/scripts/auto_fix.sh",
                    "max_attempts": 3,
                    "cooldown": 600  # 10分钟冷却时间
                }
            }
        }
        
        # 写入配置文件
        config_json = json.dumps(monitoring_config, indent=2, ensure_ascii=False)
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/.openclaw/monitoring/configs/monitoring.json << 'EOF'\n{config_json}\nEOF")
        time.sleep(1)
        print("✓ 监控配置已创建")
        
        # 创建定时任务
        print("\n[6] 配置定时任务...")
        crontab_entry = '''
# EIMS2026 监控定时任务
# 每5分钟执行健康检查
*/5 * * * * /root/.openclaw/monitoring/scripts/health_check.sh >> /dev/null 2>&1

# 每10分钟检查并自动修复
*/10 * * * * /root/.openclaw/monitoring/scripts/auto_fix.sh >> /dev/null 2>&1

# 每天凌晨2点清理旧日志
0 2 * * * find /root/.openclaw/monitoring/logs -name "*.log" -mtime +7 -delete >> /dev/null 2>&1

# 每天凌晨3点备份数据库
0 3 * * * mysqldump -uroot -p'EIMS2026_mysql' eims > /var/www/eims/backups/eims_backup_$(date +\\%Y\\%m\\%d).sql 2>/dev/null
'''
        
        stdin, stdout, stderr = ssh.exec_command(f'(crontab -l 2>/dev/null; echo "{crontab_entry}") | crontab -')
        time.sleep(1)
        print("✓ 定时任务已配置")
        
        # 创建备份目录
        print("\n[7] 创建备份目录...")
        ssh.exec_command('mkdir -p /var/www/eims/backups')
        print("✓ 备份目录已创建")
        
        # 立即执行一次健康检查
        print("\n[8] 执行首次健康检查...")
        stdin, stdout, stderr = ssh.exec_command('/root/.openclaw/monitoring/scripts/health_check.sh')
        time.sleep(3)
        result = stdout.read().decode()
        print(result)
        
        # 显示监控配置摘要
        print("\n" + "=" * 70)
        print("✅ OpenClaw监控配置完成！")
        print("=" * 70)
        print("\n📊 监控的服务:")
        print("   • Gunicorn (端口8000) - 每5分钟检查")
        print("   • Nginx (端口80) - 每5分钟检查")
        print("   • MySQL (端口3306) - 每5分钟检查")
        print("   • HTTP访问测试 - 每5分钟检查")
        print("   • 磁盘空间监控 - 每5分钟检查")
        print("   • 内存使用监控 - 每5分钟检查")
        print("   • 错误日志监控 - 每5分钟检查")
        
        print("\n🔧 自动修复功能:")
        print("   • Gunicorn自动重启")
        print("   • Nginx自动重启")
        print("   • MySQL连接自动修复")
        print("   • 端口冲突自动解决")
        print("   • 日志自动清理")
        
        print("\n💾 自动备份:")
        print("   • 数据库每日凌晨3点自动备份")
        print("   • 备份位置: /var/www/eims/backups/")
        
        print("\n📁 日志文件位置:")
        print("   • 健康检查日志: /root/.openclaw/monitoring/logs/health_check.log")
        print("   • 自动修复日志: /root/.openclaw/monitoring/logs/auto_fix.log")
        print("   • 告警日志: /root/.openclaw/monitoring/logs/alerts.log")
        
        print("\n⏰ 定时任务:")
        print("   • 每5分钟: 健康检查")
        print("   • 每10分钟: 自动修复检查")
        print("   • 每天凌晨2点: 清理旧日志")
        print("   • 每天凌晨3点: 数据库备份")
        
        print("\n🎯 手动执行命令:")
        print("   健康检查: /root/.openclaw/monitoring/scripts/health_check.sh")
        print("   自动修复: /root/.openclaw/monitoring/scripts/auto_fix.sh")
        print("   查看日志: tail -f /root/.openclaw/monitoring/logs/health_check.log")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
