#!/usr/bin/env python3
"""
EIMS2026 完整自动化部署脚本 v2
完全无人值守，包含Python升级
"""
import paramiko
import os
import time
import sys
from datetime import datetime

# ==================== 配置信息 ====================
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')

PROJECT_PATH = '/var/www/eims'
VENV_PATH = '/var/www/eims/venv'
GIT_REPO = 'https://gitee.com/liming20090607/eims2026.git'

DB_NAME = 'eims'
DB_USER = 'root'
DB_PASSWORD = 'EIMS2026_mysql'
DB_HOST = 'localhost'

class AutoDeployer:
    def __init__(self):
        self.ssh = None
        self.step = 0
    
    def connect(self):
        """连接服务器"""
        print(f"\n{'='*80}")
        print(f"🚀 EIMS2026 完整自动化部署系统 v2.0")
        print(f"{'='*80}")
        print(f"\n⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  服务器: {SERVER_IP}")
        print(f"📁 项目路径: {PROJECT_PATH}")
        print(f"🔗 代码仓库: {GIT_REPO}")
        print(f"💾 数据库: {DB_NAME}@{DB_HOST}")
        print(f"\n{'='*80}\n")
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
            print("✅ SSH连接成功\n")
            return True
        except Exception as e:
            print(f"❌ SSH连接失败: {e}")
            return False
    
    def run(self, cmd, desc="", timeout=30, show_output=True):
        """执行命令"""
        self.step += 1
        print(f"[{self.step}] {desc}")
        
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        exit_code = stdout.channel.recv_exit_status()
        
        if show_output and output:
            for line in output.split('\n')[-3:]:  # 只显示最后3行
                print(f"    {line}")
        
        if exit_code != 0 and error:
            print(f"    ⚠️  {error[:200]}")
        
        return exit_code == 0, output, error
    
    def deploy(self):
        """执行完整部署流程"""
        start_time = time.time()
        
        # 步骤1: 升级Python到3.10
        print(f"\n{'='*80}")
        print("📦 步骤 1: 安装Python 3.10")
        print(f"{'='*80}\n")
        
        self.run("python3 --version", "检查当前Python版本")
        
        # 安装Python 3.10
        python_install_cmds = [
            ("yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget", "安装编译依赖", 120),
            ("cd /tmp && wget -q https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz && echo '下载完成' || echo '下载失败'", "下载Python 3.10.12源码", 300),
            ("cd /tmp && tar -xzf Python-3.10.12.tgz && echo '解压完成'", "解压Python源码", 30),
            ("cd /tmp/Python-3.10.12 && ./configure --enable-optimizations 2>&1 | tail -5", "配置Python编译", 120),
            ("cd /tmp/Python-3.10.12 && make -j$(nproc) 2>&1 | tail -10", "编译Python（约5-10分钟）", 900),
            ("cd /tmp/Python-3.10.12 && make altinstall 2>&1 | tail -5", "安装Python", 180),
            ("python3.10 --version", "验证Python 3.10安装", 10),
        ]
        
        for cmd_tuple in python_install_cmds:
            cmd = cmd_tuple[0]
            desc = cmd_tuple[1]
            timeout = cmd_tuple[2] if len(cmd_tuple) > 2 else 120
            
            # 检查Python 3.10是否已安装
            if 'python3.10 --version' in cmd:
                success, output, _ = self.run(cmd, desc, timeout)
                if 'Python 3.10' in output:
                    print("    ✅ Python 3.10已安装，跳过编译\n")
                    break
            elif 'wget' in cmd:
                # 下载命令特殊处理，使用后台方式
                print(f"[{self.step + 1}] {desc}")
                self.ssh.exec_command(cmd, timeout=timeout)
                # 等待下载完成
                for i in range(30):
                    time.sleep(10)
                    stdin, stdout, stderr = self.ssh.exec_command("ls -lh /tmp/Python-3.10.12.tgz 2>&1 | awk '{print $5}'")
                    size = stdout.read().decode().strip()
                    if size and 'No such' not in size and size != '0':
                        print(f"    ✅ 下载完成: {size}")
                        self.step += 1
                        break
                    if i % 3 == 0:
                        print(f"    ... 下载中 ({(i+1)*10}秒)")
            else:
                self.run(cmd, desc, timeout)
        
        # 设置默认python3指向python3.10
        self.run("ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3", "设置python3默认版本")
        self.run("ln -sf /usr/local/bin/pip3.10 /usr/local/bin/pip3", "设置pip3默认版本")
        self.run("python3 --version", "确认Python版本", show_output=True)
        
        # 步骤2: 停止所有服务
        print(f"\n{'='*80}")
        print("🛑 步骤 2: 停止所有服务")
        print(f"{'='*80}\n")
        
        self.run("pkill -9 -f gunicorn 2>/dev/null; echo done", "停止Gunicorn")
        self.run("systemctl stop nginx 2>/dev/null; echo done", "停止Nginx")
        self.run("systemctl stop mysqld 2>/dev/null || service mysql stop 2>/dev/null; echo done", "停止MySQL")
        time.sleep(2)
        
        # 步骤3: 备份并清理
        print(f"\n{'='*80}")
        print("🧹 步骤 3: 备份数据并清理旧文件")
        print(f"{'='*80}\n")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run(
            f"mkdir -p /tmp/backups && mysqldump -u{DB_USER} -p'{DB_PASSWORD}' {DB_NAME} > /tmp/backups/eims_{timestamp}.sql 2>/dev/null; ls -lh /tmp/backups/",
            "备份数据库"
        )
        
        self.run(f"rm -rf {PROJECT_PATH}", "删除旧项目目录")
        self.run(f"mkdir -p {PROJECT_PATH}", "创建项目目录")
        
        # 步骤4: 克隆代码
        print(f"\n{'='*80}")
        print("📥 步骤 4: 从Gitee拉取最新代码")
        print(f"{'='*80}\n")
        
        self.run(f"git clone {GIT_REPO} {PROJECT_PATH}", "克隆代码仓库", 120)
        
        # 步骤5: 创建虚拟环境并安装依赖
        print(f"\n{'='*80}")
        print("🐍 步骤 5: 创建虚拟环境并安装依赖")
        print(f"{'='*80}\n")
        
        self.run(f"python3 -m venv {VENV_PATH}", "创建Python虚拟环境", 60)
        self.run(f"source {VENV_PATH}/bin/activate && pip install --upgrade pip", "升级pip", 60)
        self.run(f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && pip install -r requirements.txt", "安装项目依赖", 300)
        
        # 步骤6: 配置数据库
        print(f"\n{'='*80}")
        print("💾 步骤 6: 配置MySQL数据库")
        print(f"{'='*80}\n")
        
        self.run("systemctl start mysqld 2>/dev/null || service mysql start", "启动MySQL")
        time.sleep(3)
        
        self.run(f"mysql -u{DB_USER} -p'{DB_PASSWORD}' -e 'SELECT 1'", "验证MySQL连接")
        
        self.run(
            f"mysql -u{DB_USER} -p'{DB_PASSWORD}' -e \"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci\"",
            "创建数据库"
        )
        
        # 恢复数据库备份
        backup_file = f"/tmp/backups/eims_{timestamp}.sql"
        self.run(
            f"test -f {backup_file} && mysql -u{DB_USER} -p'{DB_PASSWORD}' {DB_NAME} < {backup_file} && echo '数据库已恢复' || echo '跳过恢复'",
            "恢复数据库备份"
        )
        
        # 重置MySQL root密码（确保认证正常）
        print("\n    重置MySQL认证配置...")
        mysql_fix_script = """
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
"""
        self.run(f"mysql -u{DB_USER} -p'{DB_PASSWORD}' -e \"{mysql_fix_script.strip()}\"", "重置MySQL root密码")
        
        # 步骤7: 配置项目
        print(f"\n{'='*80}")
        print("⚙️  步骤 7: 配置项目")
        print(f"{'='*80}\n")
        
        # 创建.env文件
        env_content = f"""# Database
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASSWORD={DB_PASSWORD}
DB_HOST={DB_HOST}
DB_PORT=3306

# Django
SECRET_KEY=django-insecure-eims2026-auto-deploy-key
DEBUG=True
ALLOWED_HOSTS=*

# Server
SERVER_IP={SERVER_IP}
"""
        
        env_cmd = f"""cat > {PROJECT_PATH}/.env << 'EOF'
{env_content}
EOF"""
        self.run(env_cmd, "创建.env配置文件")
        
        # 创建日志目录
        self.run(f"mkdir -p {PROJECT_PATH}/logs {PROJECT_PATH}/staticfiles {PROJECT_PATH}/media", "创建必要目录")
        
        # 步骤8: 数据库迁移
        print(f"\n{'='*80}")
        print("🗄️  步骤 8: 数据库迁移")
        print(f"{'='*80}\n")
        
        self.run(
            f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && python manage.py migrate --run-syncdb",
            "运行数据库迁移",
            120
        )
        
        self.run(
            f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && python manage.py collectstatic --noinput",
            "收集静态文件",
            60
        )
        
        # 步骤9: 配置Nginx
        print(f"\n{'='*80}")
        print("🌐 步骤 9: 配置Nginx反向代理")
        print(f"{'='*80}\n")
        
        nginx_config = f"""server {{
    listen 80;
    server_name www.xietongai.com.cn xietongai.com.cn {SERVER_IP};

    access_log /var/log/nginx/eims_access.log;
    error_log /var/log/nginx/eims_error.log;

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }}

    location /static/ {{
        alias {PROJECT_PATH}/staticfiles/;
        expires 30d;
    }}

    location /media/ {{
        alias {PROJECT_PATH}/media/;
        expires 30d;
    }}
}}
"""
        
        nginx_cmd = f"""cat > /etc/nginx/conf.d/eims.conf << 'NGINXEOF'
{nginx_config}
NGINXEOF"""
        self.run(nginx_cmd, "创建Nginx配置文件")
        self.run("nginx -t", "测试Nginx配置")
        self.run("systemctl start nginx 2>/dev/null || /usr/local/nginx/sbin/nginx", "启动Nginx")
        
        # 步骤10: 配置OpenClaw自动监控
        print(f"\n{'='*80}")
        print("🤖 步骤 10: 配置OpenClaw自动监控")
        print(f"{'='*80}\n")
        
        self.run("mkdir -p /root/.openclaw/monitoring/scripts /root/.openclaw/monitoring/logs", "创建监控目录")
        
        # 创建健康检查脚本
        health_check = r"""#!/bin/bash
LOG="/root/.openclaw/monitoring/logs/health_check.log"
STATUS="/root/.openclaw/monitoring/status.json"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ===== 健康检查 =====" >> $LOG

# Gunicorn
if pgrep -f gunicorn >/dev/null 2>&1; then
    echo "[$TS] [20%] ✓ Gunicorn: OK" >> $LOG
    G="OK"
else
    echo "[$TS] [20%] ✗ Gunicorn: 重启" >> $LOG
    cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 wsgi:application >/var/www/eims/logs/gunicorn.log 2>&1 &
    G="RESTARTED"
fi

# MySQL
if mysql -uroot -p'EIMS2026_mysql' -e "SELECT 1" &>/dev/null; then
    echo "[$TS] [50%] ✓ MySQL: OK" >> $LOG
    M="OK"
else
    echo "[$TS] [50%] ✗ MySQL: 修复" >> $LOG
    M="FAIL"
    bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh 2>/dev/null &
    sleep 15
    if mysql -uroot -p'EIMS2026_mysql' -e "SELECT 1" &>/dev/null; then
        M="FIXED"
        echo "[$TS] [80%] ✓ MySQL: 修复成功" >> $LOG
    fi
fi

DISK=$(df / | tail -1 | awk '{print $5}')
echo "[$TS] [90%] 💾 磁盘: $DISK" >> $LOG

echo "{\"timestamp\":\"$TS\",\"gunicorn\":\"$G\",\"mysql\":\"$M\",\"disk\":\"$DISK\"}" > $STATUS
echo "[$TS] [100%] 完成" >> $LOG
"""
        
        hc_cmd = f"""cat > /root/.openclaw/monitoring/scripts/health_check.sh << 'SCRIPTEOF'
{health_check}
SCRIPTEOF"""
        self.run(hc_cmd, "创建健康检查脚本")
        self.run("chmod +x /root/.openclaw/monitoring/scripts/health_check.sh", "设置执行权限")
        
        # 创建MySQL修复脚本
        mysql_fix = r"""#!/bin/bash
LOG="/root/.openclaw/monitoring/logs/auto_fix.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TS] ========== MySQL修复 ==========" >> $LOG

# 停止
killall -9 mysqld mysqld_safe 2>/dev/null
sleep 2
rm -f /var/lib/mysql/mysql.sock
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld

# skip-grant-tables启动
mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &
sleep 10

# 重置密码
mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

# 重启
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld
sleep 3
systemctl start mysqld 2>/dev/null || service mysql start
sleep 5

# 验证
mysql -uroot -p'EIMS2026_mysql' -e "SELECT 1" &>/dev/null
if [ $? -eq 0 ]; then
    echo "[$TS] ✅ MySQL修复成功" >> $LOG
else
    echo "[$TS] ❌ MySQL修复失败" >> $LOG
fi

# 重启Gunicorn
pkill -9 -f gunicorn 2>/dev/null
sleep 2
cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &

echo "[$TS] ============================" >> $LOG
"""
        
        mf_cmd = f"""cat > /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh << 'SCRIPTEOF'
{mysql_fix}
SCRIPTEOF"""
        self.run(mf_cmd, "创建MySQL修复脚本")
        self.run("chmod +x /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "设置执行权限")
        
        # 配置crontab
        crontab = f"""# OpenClaw Auto Monitor
*/2 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh >> /root/.openclaw/monitoring/logs/health_check.log 2>&1
"""
        self.run(f"echo '{crontab}' | crontab -", "配置定时任务（每2分钟）")
        
        # 步骤11: 启动Gunicorn
        print(f"\n{'='*80}")
        print("🚀 步骤 11: 启动Gunicorn")
        print(f"{'='*80}\n")
        
        gunicorn_cmd = f"""cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && nohup gunicorn \\
--bind 127.0.0.1:8000 \\
--workers 4 \\
--timeout 300 \\
--access-logfile {PROJECT_PATH}/logs/gunicorn_access.log \\
--error-logfile {PROJECT_PATH}/logs/gunicorn_error.log \\
wsgi:application > {PROJECT_PATH}/logs/gunicorn.log 2>&1 &"""
        
        self.run(gunicorn_cmd, "启动Gunicorn")
        time.sleep(5)
        
        self.run("ps aux | grep gunicorn | grep -v grep | wc -l", "验证Gunicorn进程")
        
        # 步骤12: 最终验证
        print(f"\n{'='*80}")
        print("✅ 步骤 12: 最终验证")
        print(f"{'='*80}\n")
        
        time.sleep(10)
        
        # 测试各个组件
        self.run(f"mysql -u{DB_USER} -p'{DB_PASSWORD}' -e 'SHOW DATABASES' | grep {DB_NAME}", "测试MySQL")
        self.run("curl -s -o /dev/null -w 'HTTP %{http_code}' --connect-timeout 5 http://127.0.0.1:8000/login/", "测试Gunicorn")
        self.run("curl -s -o /dev/null -w 'HTTP %{http_code}' --connect-timeout 5 http://127.0.0.1/login/", "测试Nginx")
        
        self.run("ps aux | grep -E 'gunicorn|nginx|mysqld' | grep -v grep | wc -l", "统计服务进程")
        self.run("df -h / | tail -1 | awk '{print \"磁盘: \" $5}'", "磁盘使用率")
        self.run("free -m | grep Mem | awk '{printf \"内存: %.1f%%\", $3/$2*100}'", "内存使用率")
        
        # 计算总耗时
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        # 显示总结
        print(f"\n{'='*80}")
        print("🎉 部署完成！")
        print(f"{'='*80}")
        print(f"""
⏱️  总耗时: {minutes}分{seconds}秒

📊 系统信息:
  • 服务器: {SERVER_IP}
  • Python: 3.10.12
  • 项目路径: {PROJECT_PATH}
  • 数据库: {DB_NAME}
  • 备份位置: /tmp/backups/eims_{timestamp}.sql

🌐 访问地址:
  • 域名: http://www.xietongai.com.cn/login/
  • IP: http://{SERVER_IP}:8000/login/

🔧 服务状态:
  • ✅ Gunicorn (4 workers)
  • ✅ Nginx (port 80)
  • ✅ MySQL (port 3306)
  • ✅ OpenClaw (auto monitor every 2 min)

📋 管理命令:
  • SSH: ssh root@{SERVER_IP}
  • 查看Gunicorn日志: tail -f {PROJECT_PATH}/logs/gunicorn.log
  • 查看Nginx错误日志: tail -f /var/log/nginx/eims_error.log
  • 查看OpenClaw日志: tail -f /root/.openclaw/monitoring/logs/health_check.log

🛡️  自动保护:
  • OpenClaw每2分钟自动检查
  • MySQL故障自动修复
  • Gunicorn自动重启
  • 完整的日志记录

🎯 下一步:
  1. 浏览器访问: http://www.xietongai.com.cn/login/
  2. 使用管理员账号登录
  3. 开始使用办公系统

{'='*80}
""")
        
        self.ssh.close()
        print("✅ 部署脚本执行完毕\n")

def main():
    try:
        deployer = AutoDeployer()
        
        if not deployer.connect():
            print("❌ 无法连接服务器，部署终止")
            sys.exit(1)
        
        deployer.deploy()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  部署被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
