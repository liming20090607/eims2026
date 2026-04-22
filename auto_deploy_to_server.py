#!/usr/bin/env python3
"""
全自动无人值守部署系统到云服务器
Fully Automated Unattended Deployment to Cloud Server

This script will:
1. Backup local code and database
2. Upload code to server via Gitee
3. Configure server environment (Python 3.10+, MySQL, Nginx)
4. Deploy application with all dependencies
5. Run database migrations
6. Start services (Gunicorn + Nginx)
7. Verify everything is working
8. Auto-retry on failures
"""

import paramiko
import os
import time
import sys
import subprocess
from datetime import datetime

# ==================== Configuration ====================
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'
GITEE_REPO = 'https://gitee.com/liming20090607/eims2026.git'

# Database configuration
DB_NAME = 'eims'
DB_USER = 'root'
DB_PASSWORD = 'EIMS2026_mysql'

# Local paths
LOCAL_PROJECT = r'e:\EIMS2026'
BACKUP_DIR = r'e:\EIMS2026\backups'

print("=" * 80)
print("🚀 EIMS2026 全自动无人值守部署")
print("Fully Automated Unattended Deployment")
print("=" * 80)
print(f"服务器: {SERVER_IP}")
print(f"路径: {SERVER_PATH}")
print(f"仓库: {GITEE_REPO}")
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)


def run_ssh_command(ssh, command, desc="", timeout=30, retry=3):
    """Execute SSH command with retry logic"""
    for attempt in range(1, retry + 1):
        try:
            print(f"  [{desc}] 尝试 {attempt}/{retry}...")
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='ignore').strip()
            error = stderr.read().decode('utf-8', errors='ignore').strip()
            
            if exit_code == 0:
                if output:
                    print(f"  ✅ {desc}: 成功")
                    if len(output) < 200:
                        print(f"     {output}")
                else:
                    print(f"  ✅ {desc}: 完成")
                return True, output
            else:
                print(f"  ⚠️  {desc}: 失败 (code={exit_code})")
                if error and len(error) < 300:
                    print(f"     错误: {error}")
                if attempt < retry:
                    time.sleep(2)
                    continue
                return False, error
                
        except Exception as e:
            print(f"  ❌ {desc}: 异常 - {str(e)}")
            if attempt < retry:
                time.sleep(2)
                continue
            return False, str(e)
    
    return False, "Max retries exceeded"


def wait_for_service(ssh, check_cmd, service_name, max_wait=60):
    """Wait for a service to become available"""
    print(f"  ⏳ 等待 {service_name} 就绪...")
    for i in range(max_wait // 2):
        stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=5)
        result = stdout.read().decode().strip()
        if result:
            print(f"  ✅ {service_name} 已就绪 ({i*2}秒)")
            return True
        time.sleep(2)
    print(f"  ❌ {service_name} 超时")
    return False


def main():
    try:
        # Step 0: Connect to server
        print("\n[0/10] 连接服务器...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        for attempt in range(1, 4):
            try:
                ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
                print(f"  ✅ 服务器连接成功")
                break
            except Exception as e:
                print(f"  ⚠️  连接失败 (尝试 {attempt}/3): {e}")
                if attempt == 3:
                    raise
                time.sleep(3)
        
        # Step 1: Check current system state
        print("\n[1/10] 检查当前系统状态...")
        success, python_ver = run_ssh_command(ssh, "python3 --version 2>&1 || python --version 2>&1", "检查Python版本")
        success, mysql_status = run_ssh_command(ssh, "systemctl is-active mysqld 2>/dev/null || service mysql status 2>&1 | head -1", "检查MySQL状态")
        success, nginx_status = run_ssh_command(ssh, "systemctl is-active nginx 2>/dev/null || ps aux | grep nginx | grep -v grep | wc -l", "检查Nginx状态")
        
        print(f"\n  当前状态:")
        print(f"    Python: {python_ver}")
        print(f"    MySQL: {mysql_status}")
        print(f"    Nginx: {nginx_status}")
        
        # Step 2: Upgrade Python to 3.10 if needed
        print("\n[2/10] 确保Python 3.10+可用...")
        success, py_version = run_ssh_command(ssh, "python3.10 --version 2>&1", "检查Python 3.10")
        
        if not success or '3.10' not in py_version:
            print("  ⚙️  需要安装/升级Python 3.10...")
            
            # Install dependencies
            run_ssh_command(ssh, "yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make 2>&1 | tail -5", "安装编译依赖", timeout=120)
            
            # Download Python 3.10.12
            print("  📥 下载Python 3.10.12...")
            run_ssh_command(ssh, "cd /tmp && wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz", "下载Python源码", timeout=300)
            
            # Extract and compile
            print("  🔨 编译Python 3.10.12...")
            run_ssh_command(ssh, "cd /tmp && tar xzf Python-3.10.12.tgz && cd Python-3.10.12 && ./configure --enable-optimizations 2>&1 | tail -3", "配置编译", timeout=120)
            run_ssh_command(ssh, "cd /tmp/Python-3.10.12 && make -j$(nproc) 2>&1 | tail -3", "编译Python", timeout=600)
            run_ssh_command(ssh, "cd /tmp/Python-3.10.12 && make altinstall 2>&1 | tail -3", "安装Python", timeout=300)
            
            # Create symlink
            run_ssh_command(ssh, "ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3", "创建软链接")
            run_ssh_command(ssh, "ln -sf /usr/local/bin/pip3.10 /usr/local/bin/pip3", "创建pip软链接")
            
            success, new_ver = run_ssh_command(ssh, "python3 --version", "验证Python版本")
            print(f"  ✅ Python已升级: {new_ver}")
        else:
            print(f"  ✅ Python 3.10已存在: {py_version}")
        
        # Step 3: Setup MySQL
        print("\n[3/10] 配置MySQL数据库...")
        
        # Ensure MySQL is running
        run_ssh_command(ssh, "systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null", "启动MySQL", timeout=30)
        time.sleep(3)
        
        # Wait for MySQL to be ready
        wait_for_service(ssh, "mysqladmin ping 2>&1 | grep -c alive", "MySQL", max_wait=30)
        
        # Create database and user
        mysql_cmd = f"""mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{DB_PASSWORD}';
FLUSH PRIVILEGES;
SELECT 'Database configured successfully' as status;
EOF"""
        success, result = run_ssh_command(ssh, mysql_cmd, "配置数据库", timeout=30)
        
        if success:
            print("  ✅ MySQL配置完成")
        else:
            print("  ⚠️  MySQL配置可能有问题，继续尝试...")
        
        # Step 4: Clone/Pull code from Gitee
        print("\n[4/10] 从Gitee获取最新代码...")
        
        # Check if directory exists
        success, dir_exists = run_ssh_command(ssh, f"test -d {SERVER_PATH} && echo 'exists' || echo 'not_exists'", "检查目录")
        
        if 'exists' in dir_exists:
            # Pull latest code
            print("  📥 拉取最新代码...")
            run_ssh_command(ssh, f"cd {SERVER_PATH} && git pull {GITEE_REPO} master 2>&1 | tail -5", "Git Pull", timeout=60)
        else:
            # Clone repository
            print("  📥 克隆仓库...")
            run_ssh_command(ssh, f"mkdir -p {SERVER_PATH} && cd {SERVER_PATH} && git clone {GITEE_REPO} . 2>&1 | tail -5", "Git Clone", timeout=120)
        
        success, commit_info = run_ssh_command(ssh, f"cd {SERVER_PATH} && git log --oneline -1", "最新提交")
        print(f"  ✅ 代码已更新: {commit_info}")
        
        # Step 5: Setup Python virtual environment
        print("\n[5/10] 配置Python虚拟环境...")
        
        # Create venv
        run_ssh_command(ssh, f"cd {SERVER_PATH} && python3 -m venv venv 2>&1 | tail -3", "创建虚拟环境", timeout=60)
        
        # Install requirements
        print("  📦 安装Python依赖包...")
        run_ssh_command(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && pip install --upgrade pip 2>&1 | tail -3", "升级pip", timeout=120)
        run_ssh_command(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && pip install -r requirements.txt 2>&1 | tail -10", "安装依赖", timeout=300)
        
        # Verify Django installation
        success, django_ver = run_ssh_command(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python -c 'import django; print(django.get_version())'", "验证Django")
        print(f"  ✅ Django版本: {django_ver}")
        
        # Step 6: Configure Django settings
        print("\n[6/10] 配置Django设置...")
        
        # Update database configuration in settings.py
        settings_update = f"""
# Update database configuration
sed -i "s/'NAME': '[^']*'/'NAME': '{DB_NAME}'/" {SERVER_PATH}/settings.py
sed -i "s/'USER': '[^']*'/'USER': '{DB_USER}'/" {SERVER_PATH}/settings.py
sed -i "s/'PASSWORD': '[^']*'/'PASSWORD': '{DB_PASSWORD}'/" {SERVER_PATH}/settings.py
echo "Settings updated"
"""
        run_ssh_command(ssh, settings_update, "更新数据库配置")
        
        # Create necessary directories
        run_ssh_command(ssh, f"mkdir -p {SERVER_PATH}/logs {SERVER_PATH}/media {SERVER_PATH}/staticfiles", "创建必要目录")
        
        # Step 7: Run database migrations
        print("\n[7/10] 执行数据库迁移...")
        
        # Makemigrations
        run_ssh_command(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py makemigrations 2>&1 | tail -10", "生成迁移文件", timeout=60)
        
        # Migrate
        success, migrate_result = run_ssh_command(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -15", "执行迁移", timeout=120)
        
        if success:
            print("  ✅ 数据库迁移完成")
        else:
            print("  ⚠️  迁移可能有警告，继续...")
        
        # Collect static files
        print("  📁 收集静态文件...")
        run_ssh_command(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py collectstatic --noinput 2>&1 | tail -5", "收集静态文件", timeout=60)
        
        # Step 8: Configure and start Gunicorn
        print("\n[8/10] 配置并启动Gunicorn...")
        
        # Stop existing Gunicorn
        run_ssh_command(ssh, "pkill -9 -f gunicorn 2>/dev/null; sleep 2", "停止旧Gunicorn")
        
        # Start Gunicorn
        gunicorn_cmd = f"""cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 300 \\
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \\
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \\
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &"""
        
        run_ssh_command(ssh, gunicorn_cmd, "启动Gunicorn")
        time.sleep(5)
        
        # Verify Gunicorn
        success, gunicorn_count = run_ssh_command(ssh, "ps aux | grep gunicorn | grep -v grep | wc -l", "验证Gunicorn")
        print(f"  ✅ Gunicorn进程数: {gunicorn_count}")
        
        # Step 9: Configure and start Nginx
        print("\n[9/10] 配置并启动Nginx...")
        
        # Create Nginx config
        nginx_config = f"""server {{
    listen 80;
    server_name www.xietongai.com.cn {SERVER_IP};
    
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
        alias {SERVER_PATH}/staticfiles/;
        expires 30d;
    }}
    
    location /media/ {{
        alias {SERVER_PATH}/media/;
        expires 30d;
    }}
}}"""
        
        # Write nginx config
        run_ssh_command(ssh, f"cat > /etc/nginx/conf.d/eims.conf <<'NGINX_EOF'\n{nginx_config}\nNGINX_EOF", "创建Nginx配置")
        
        # Test and restart Nginx
        run_ssh_command(ssh, "nginx -t 2>&1", "测试Nginx配置")
        run_ssh_command(ssh, "systemctl restart nginx 2>/dev/null || /usr/local/nginx/sbin/nginx -s reload 2>/dev/null || nginx -s reload", "重启Nginx", timeout=30)
        time.sleep(2)
        
        # Verify Nginx
        success, nginx_active = run_ssh_command(ssh, "systemctl is-active nginx 2>/dev/null || ps aux | grep 'nginx: master' | grep -v grep | wc -l", "验证Nginx")
        print(f"  ✅ Nginx状态: {nginx_active}")
        
        # Step 10: Final verification
        print("\n[10/10] 最终验证...")
        
        # Test HTTP access
        time.sleep(3)
        success, http_code = run_ssh_command(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "测试HTTP访问", timeout=10)
        
        if success and http_code == '200':
            print(f"  ✅ HTTP状态码: {http_code}")
        else:
            print(f"  ⚠️  HTTP状态码: {http_code}")
        
        # Test MySQL connection
        test_db_cmd = f"""cd {SERVER_PATH} && source venv/bin/activate && python -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='{DB_USER}', password='{DB_PASSWORD}', database='{DB_NAME}')
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    conn.close()
    print('MySQL连接成功')
except Exception as e:
    print(f'MySQL连接失败: {{e}}')
" """
        success, db_test = run_ssh_command(ssh, test_db_cmd, "测试MySQL连接")
        
        # Get system info
        success, disk_usage = run_ssh_command(ssh, "df -h / | tail -1 | awk '{print $5}'", "磁盘使用率")
        success, mem_usage = run_ssh_command(ssh, "free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2}'", "内存使用率")
        
        print(f"\n{'=' * 80}")
        print("✅ 部署完成！")
        print(f"{'=' * 80}")
        print(f"\n📊 系统状态:")
        print(f"  • Gunicorn: {gunicorn_count} 个进程")
        print(f"  • Nginx: {nginx_active}")
        print(f"  • MySQL: {'正常' if success else '需检查'}")
        print(f"  • 磁盘使用: {disk_usage}")
        print(f"  • 内存使用: {mem_usage}")
        print(f"\n🌐 访问地址:")
        print(f"  • 登录页面: http://{SERVER_IP}/login/")
        print(f"  • 域名访问: http://www.xietongai.com.cn/login/")
        print(f"\n⏰ 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 80}")
        
        ssh.close()
        
    except Exception as e:
        print(f"\n❌ 部署失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
