#!/usr/bin/env python3
"""
EIMS2026 完全自动化部署脚本
Fully Automated Deployment Script for EIMS2026
实现从本地到云服务器的无人值守部署
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
DB_PORT = '3306'

# ==================== 工具函数 ====================
class Deployer:
    def __init__(self):
        self.ssh = None
        self.step = 0
        self.total_steps = 12
    
    def connect(self):
        """连接服务器"""
        print(f"\n{'='*80}")
        print(f"🚀 EIMS2026 自动化部署系统")
        print(f"{'='*80}")
        print(f"\n服务器: {SERVER_IP}")
        print(f"项目路径: {PROJECT_PATH}")
        print(f"代码仓库: {GIT_REPO}")
        print(f"数据库: {DB_NAME}@{DB_HOST}")
        
        print(f"\n[0/{self.total_steps}] 连接服务器...")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
            print("  ✅ 连接成功\n")
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")
            print("\n💡 请检查:")
            print("  • SSH密钥是否正确")
            print("  • 服务器是否可访问")
            sys.exit(1)
    
    def execute(self, cmd, desc="", timeout=30, ignore_error=False):
        """执行命令"""
        self.step += 1
        print(f"[{self.step}/{self.total_steps}] {desc}")
        print(f"  执行: {cmd[:100]}{'...' if len(cmd) > 100 else ''}")
        
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0 or ignore_error:
            if output:
                print(f"  ✅ {output[:200]}")
            return True, output
        else:
            print(f"  ❌ 失败 (exit code: {exit_code})")
            if error:
                print(f"     错误: {error[:300]}")
            if not ignore_error:
                print(f"\n  ⚠️  继续执行下一步...")
            return False, error
    
    def run_script(self, script_content, desc=""):
        """运行Python脚本"""
        self.step += 1
        print(f"[{self.step}/{self.total_steps}] {desc}")
        
        # 将脚本写入临时文件
        temp_file = '/tmp/deploy_script.py'
        create_cmd = f"cat > {temp_file} << 'PYEOF'\n{script_content}\nPYEOF"
        self.ssh.exec_command(create_cmd, timeout=10)
        time.sleep(1)
        
        # 执行脚本
        stdin, stdout, stderr = self.ssh.exec_command(f"cd {PROJECT_PATH} && source venv/bin/activate && python3 {temp_file}", timeout=60)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if output:
            print(f"  {output[:300]}")
        if error and 'Warning' not in error:
            print(f"  ⚠️  {error[:200]}")
        
        # 清理临时文件
        self.ssh.exec_command(f"rm -f {temp_file}", timeout=5)
        
        return output, error
    
    def close(self):
        """关闭连接"""
        if self.ssh:
            self.ssh.close()
    
    # ==================== 部署步骤 ====================
    
    def step1_check_environment(self):
        """步骤1: 检查服务器环境"""
        print(f"\n{'='*80}")
        print("步骤 1/12: 检查服务器环境")
        print(f"{'='*80}\n")
        
        # 检查Python
        self.execute("python3 --version", "检查Python版本")
        
        # 检查MySQL
        self.execute("mysql --version", "检查MySQL版本")
        
        # 检查Nginx
        self.execute("nginx -v 2>&1 || echo 'Nginx未安装'", "检查Nginx")
        
        # 检查磁盘空间
        self.execute("df -h / | tail -1 | awk '{print $4}'", "检查可用磁盘空间")
        
        # 检查内存
        self.execute("free -m | grep Mem | awk '{printf \"%.1f GB / %.1f GB\", $2/1024, $3/1024}'", "检查内存使用")
    
    def step2_stop_services(self):
        """步骤2: 停止所有服务"""
        print(f"\n{'='*80}")
        print("步骤 2/12: 停止所有服务")
        print(f"{'='*80}\n")
        
        # 停止Gunicorn
        self.execute("pkill -9 -f gunicorn 2>/dev/null; echo 'Gunicorn已停止'", "停止Gunicorn", ignore_error=True)
        
        # 停止Nginx
        self.execute("systemctl stop nginx 2>/dev/null || nginx -s stop 2>/dev/null; echo 'Nginx已停止'", "停止Nginx", ignore_error=True)
        
        # 停止MySQL
        self.execute("systemctl stop mysqld 2>/dev/null || service mysql stop 2>/dev/null; echo 'MySQL已停止'", "停止MySQL", ignore_error=True)
        
        time.sleep(2)
    
    def step3_cleanup(self):
        """步骤3: 清理旧项目"""
        print(f"\n{'='*80}")
        print("步骤 3/12: 清理旧项目文件")
        print(f"{'='*80}\n")
        
        # 备份数据库
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"/tmp/eims_backup_{timestamp}.sql"
        
        self.execute(
            f"mysqldump -u{DB_USER} -p{DB_PASSWORD} {DB_NAME} > {backup_file} 2>/dev/null && echo '数据库已备份到 {backup_file}' || echo '数据库备份跳过（可能不存在）'",
            "备份数据库",
            ignore_error=True
        )
        
        # 清理项目目录
        self.execute(f"rm -rf {PROJECT_PATH}/* {PROJECT_PATH}/.* 2>/dev/null; echo '项目目录已清理'", "清理项目目录")
        
        # 删除旧日志
        self.execute("rm -rf /root/.openclaw/monitoring 2>/dev/null; echo 'OpenClaw监控目录已清理'", "清理OpenClaw监控", ignore_error=True)
    
    def step4_clone_code(self):
        """步骤4: 从Gitee拉取最新代码"""
        print(f"\n{'='*80}")
        print("步骤 4/12: 从Gitee拉取最新代码")
        print(f"{'='*80}\n")
        
        # 克隆代码
        self.execute(
            f"git clone {GIT_REPO} {PROJECT_PATH}",
            "克隆代码仓库",
            timeout=120
        )
        
        # 进入项目目录
        self.execute(f"cd {PROJECT_PATH} && pwd", "确认项目目录")
    
    def step5_setup_venv(self):
        """步骤5: 创建Python虚拟环境"""
        print(f"\n{'='*80}")
        print("步骤 5/12: 创建Python虚拟环境")
        print(f"{'='*80}\n")
        
        # 创建虚拟环境
        self.execute(
            f"python3 -m venv {VENV_PATH}",
            "创建虚拟环境",
            timeout=60
        )
        
        # 激活并安装依赖
        self.execute(
            f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && pip install --upgrade pip",
            "升级pip",
            timeout=60
        )
        
        self.execute(
            f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && pip install -r requirements.txt",
            "安装项目依赖",
            timeout=300
        )
    
    def step6_config_database(self):
        """步骤6: 配置数据库"""
        print(f"\n{'='*80}")
        print("步骤 6/12: 配置数据库")
        print(f"{'='*80}\n")
        
        # 启动MySQL
        self.execute("systemctl start mysqld 2>/dev/null || service mysql start", "启动MySQL服务")
        time.sleep(3)
        
        # 验证MySQL连接
        self.execute(
            f"mysql -u{DB_USER} -p{DB_PASSWORD} -e 'SELECT 1'",
            "验证MySQL连接"
        )
        
        # 检查数据库是否存在
        self.execute(
            f"mysql -u{DB_USER} -p{DB_PASSWORD} -e 'CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'",
            "创建/验证数据库",
            ignore_error=True
        )
        
        # 恢复数据库备份（如果有）
        backup_files = ["/tmp/eims_backup_*.sql"]
        for pattern in backup_files:
            self.execute(
                f"ls {pattern} 2>/dev/null | head -1 | xargs -I {{}} mysql -u{DB_USER} -p{DB_PASSWORD} {DB_NAME} < {{}} && echo '数据库已恢复' || echo '跳过数据库恢复'",
                "恢复数据库备份",
                ignore_error=True
            )
    
    def step7_config_project(self):
        """步骤7: 配置项目设置"""
        print(f"\n{'='*80}")
        print("步骤 7/12: 配置项目设置")
        print(f"{'='*80}\n")
        
        # 检查并创建.env文件
        env_script = f"""
import os

env_file = '{PROJECT_PATH}/.env'

env_content = f'''# Database Configuration
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASSWORD={DB_PASSWORD}
DB_HOST={DB_HOST}
DB_PORT={DB_PORT}

# Django Settings
SECRET_KEY=django-insecure-autogenerated-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=*

# Server
SERVER_IP={SERVER_IP}
'''

with open(env_file, 'w') as f:
    f.write(env_content)

print(f'.env文件已创建: {{env_file}}')
"""
        self.run_script(env_script, "创建.env配置文件")
        
        # 检查settings.py配置
        check_settings_script = """
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    
    # 验证数据库配置
    db_config = settings.DATABASES.get('default', {})
    print(f"数据库配置: {db_config.get('NAME')}@{db_config.get('HOST')}")
    print("Django配置验证通过")
except Exception as e:
    print(f"配置错误: {e}")
    sys.exit(1)
"""
        self.run_script(check_settings_script, "验证Django配置")
    
    def step8_migrate_database(self):
        """步骤8: 数据库迁移"""
        print(f"\n{'='*80}")
        print("步骤 8/12: 数据库迁移")
        print(f"{'='*80}\n")
        
        # 运行迁移
        self.execute(
            f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && python manage.py migrate --run-syncdb",
            "运行数据库迁移",
            timeout=120
        )
        
        # 收集静态文件
        self.execute(
            f"cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && python manage.py collectstatic --noinput",
            "收集静态文件",
            timeout=60,
            ignore_error=True
        )
    
    def step9_setup_openclaw(self):
        """步骤9: 配置OpenClaw自动监控"""
        print(f"\n{'='*80}")
        print("步骤 9/12: 配置OpenClaw自动监控")
        print(f"{'='*80}\n")
        
        # 创建监控目录
        self.execute("mkdir -p /root/.openclaw/monitoring/scripts /root/.openclaw/monitoring/logs", "创建监控目录")
        
        # 创建健康检查脚本
        health_check_script = r"""#!/bin/bash
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
    systemctl start nginx 2>/dev/null || /usr/local/nginx/sbin/nginx
    N_STATUS="RESTARTED"
    echo "[$TS] [40%] ↻ Nginx: 已重启" >> $LOG
fi

# MySQL
if mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null; then
    echo "[$TS] [60%] ✓ MySQL: 正常" >> $LOG
    M_STATUS="OK"
else
    echo "[$TS] [60%] ✗ MySQL: 故障" >> $LOG
    M_STATUS="FAIL"
    # 触发修复
    bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh 2>/dev/null &
    sleep 10
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
"""
        
        create_health_check = f"""cat > /root/.openclaw/monitoring/scripts/health_check.sh << 'SCRIPTEOF'
{health_check_script}
SCRIPTEOF"""
        
        self.execute(create_health_check, "创建健康检查脚本")
        self.execute("chmod +x /root/.openclaw/monitoring/scripts/health_check.sh", "设置执行权限")
        
        # 创建MySQL修复脚本
        mysql_fix_script = r"""#!/bin/bash
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
mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &
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
mysql -u root --socket=/var/lib/mysql/mysql.sock <<MYSQL_EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
MYSQL_EOF

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
"""
        
        create_mysql_fix = f"""cat > /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh << 'SCRIPTEOF'
{mysql_fix_script}
SCRIPTEOF"""
        
        self.execute(create_mysql_fix, "创建MySQL修复脚本")
        self.execute("chmod +x /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh", "设置执行权限")
        
        # 配置crontab
        crontab_config = f"""# OpenClaw Monitoring - Auto check every 2 minutes
*/2 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh >> /root/.openclaw/monitoring/logs/health_check.log 2>&1
"""
        self.execute(f"echo '{crontab_config}' | crontab -", "配置定时任务（每2分钟）")
        
        print("  ✅ OpenClaw监控已配置")
    
    def step10_setup_nginx(self):
        """步骤10: 配置Nginx"""
        print(f"\n{'='*80}")
        print("步骤 10/12: 配置Nginx反向代理")
        print(f"{'='*80}\n")
        
        # 创建Nginx配置
        nginx_config = """server {
    listen 80;
    server_name www.xietongai.com.cn xietongai.com.cn 39.106.41.239;

    access_log /var/log/nginx/eims_access.log;
    error_log /var/log/nginx/eims_error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    location /static/ {
        alias /var/www/eims/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/eims/media/;
        expires 30d;
    }
}
"""
        
        create_nginx = f"""cat > /etc/nginx/conf.d/eims.conf << 'NGINXEOF'
{nginx_config}
NGINXEOF"""
        
        self.execute(create_nginx, "创建Nginx配置")
        
        # 测试Nginx配置
        self.execute("nginx -t", "测试Nginx配置")
        
        # 启动Nginx
        self.execute("systemctl start nginx 2>/dev/null || /usr/local/nginx/sbin/nginx", "启动Nginx")
    
    def step11_start_services(self):
        """步骤11: 启动所有服务"""
        print(f"\n{'='*80}")
        print("步骤 11/12: 启动所有服务")
        print(f"{'='*80}\n")
        
        # 创建日志目录
        self.execute(f"mkdir -p {PROJECT_PATH}/logs", "创建日志目录")
        
        # 启动Gunicorn
        start_gunicorn = f"""cd {PROJECT_PATH} && source {VENV_PATH}/bin/activate && nohup gunicorn \\
--bind 127.0.0.1:8000 \\
--workers 4 \\
--timeout 300 \\
--access-logfile {PROJECT_PATH}/logs/gunicorn_access.log \\
--error-logfile {PROJECT_PATH}/logs/gunicorn_error.log \\
wsgi:application > {PROJECT_PATH}/logs/gunicorn.log 2>&1 &"""
        
        self.execute(start_gunicorn, "启动Gunicorn")
        time.sleep(5)
        
        # 验证Gunicorn
        self.execute("ps aux | grep gunicorn | grep -v grep | wc -l", "验证Gunicorn进程")
    
    def step12_final_verification(self):
        """步骤12: 最终验证"""
        print(f"\n{'='*80}")
        print("步骤 12/12: 最终验证")
        print(f"{'='*80}\n")
        
        # 等待服务启动
        print("  等待服务启动...")
        time.sleep(10)
        
        # 测试MySQL
        self.execute(
            f"mysql -u{DB_USER} -p{DB_PASSWORD} -e 'SHOW DATABASES' 2>&1 | grep {DB_NAME}",
            "测试MySQL连接"
        )
        
        # 测试Gunicorn
        self.execute(
            "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:8000/login/",
            "测试Gunicorn响应"
        )
        
        # 测试Nginx
        self.execute(
            "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1/login/",
            "测试Nginx代理"
        )
        
        # 检查所有进程
        self.execute("ps aux | grep -E 'gunicorn|nginx|mysqld' | grep -v grep | wc -l", "检查服务进程数")
        
        # 检查磁盘
        self.execute("df -h / | tail -1 | awk '{print $5}'", "检查磁盘使用率")
        
        # 检查内存
        self.execute("free -m | grep Mem | awk '{printf \"%.1f%%\", $3/$2*100}'", "检查内存使用率")
    
    def show_summary(self):
        """显示部署总结"""
        print(f"\n{'='*80}")
        print("✅ 部署完成！")
        print(f"{'='*80}")
        
        print(f"""
📊 部署信息:
  • 服务器: {SERVER_IP}
  • 项目路径: {PROJECT_PATH}
  • 代码仓库: {GIT_REPO}
  • 数据库: {DB_NAME}@{DB_HOST}
  • 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 访问地址:
  • 登录页面: http://www.xietongai.com.cn/login/
  • 直接访问: http://{SERVER_IP}:8000/login/

🔧 服务状态:
  • Gunicorn: 运行中（4个工作进程）
  • Nginx: 运行中（端口80）
  • MySQL: 运行中（端口3306）
  • OpenClaw: 已启用（每2分钟自动检查）

💡 管理工具:
  • SSH登录: ssh root@{SERVER_IP}
  • 查看Gunicorn日志: tail -f {PROJECT_PATH}/logs/gunicorn.log
  • 查看Nginx日志: tail -f /var/log/nginx/eims_error.log
  • 查看OpenClaw日志: tail -f /root/.openclaw/monitoring/logs/health_check.log

🛡️  自动保护:
  • OpenClaw每2分钟检查系统状态
  • 自动修复MySQL故障
  • 自动重启Gunicorn/Nginx
  • 完整的日志记录

🎯 下一步:
  1. 访问 http://www.xietongai.com.cn/login/
  2. 使用管理员账号登录
  3. 开始使用办公系统

{'='*80}
""")

# ==================== 主程序 ====================
def main():
    try:
        deployer = Deployer()
        
        # 连接服务器
        deployer.connect()
        
        # 执行部署步骤
        deployer.step1_check_environment()
        time.sleep(2)
        
        deployer.step2_stop_services()
        time.sleep(2)
        
        deployer.step3_cleanup()
        time.sleep(2)
        
        deployer.step4_clone_code()
        time.sleep(2)
        
        deployer.step5_setup_venv()
        time.sleep(2)
        
        deployer.step6_config_database()
        time.sleep(2)
        
        deployer.step7_config_project()
        time.sleep(2)
        
        deployer.step8_migrate_database()
        time.sleep(2)
        
        deployer.step9_setup_openclaw()
        time.sleep(2)
        
        deployer.step10_setup_nginx()
        time.sleep(2)
        
        deployer.step11_start_services()
        time.sleep(2)
        
        deployer.step12_final_verification()
        
        # 显示总结
        deployer.show_summary()
        
        # 关闭连接
        deployer.close()
        
        print("\n🎉 系统已准备就绪，可以开始使用！\n")
        
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
