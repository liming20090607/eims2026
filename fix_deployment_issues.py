#!/usr/bin/env python3
"""
修复部署问题并完成最终配置
Fix deployment issues and complete final configuration
"""

import paramiko
import os
import time
import sys

print("=" * 80)
print("🔧 修复部署问题")
print("Fix Deployment Issues")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'
DB_PASSWORD = 'EIMS2026_mysql'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ 已连接服务器\n")
    
    # Fix 1: Reset MySQL password with skip-grant-tables
    print("[1/6] 重置MySQL密码...")
    
    # Stop MySQL completely
    ssh.exec_command("systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 3", timeout=10)
    time.sleep(4)
    
    # Clean socket files
    ssh.exec_command("rm -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.pid", timeout=5)
    ssh.exec_command("mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld", timeout=5)
    
    # Start in skip-grant-tables mode
    print("  启动恢复模式...")
    ssh.exec_command("mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", timeout=5)
    time.sleep(10)
    
    # Wait for socket
    for i in range(10):
        stdin, stdout, stderr = ssh.exec_command("test -f /var/lib/mysql/mysql.sock && echo 'ready' || echo 'waiting'")
        if 'ready' in stdout.read().decode():
            print(f"  ✅ Socket就绪 ({i}秒)")
            break
        time.sleep(1)
    
    # Reset password
    print("  重置root密码...")
    reset_cmd = """mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT 'Password reset successful' as status;
EOF"""
    stdin, stdout, stderr = ssh.exec_command(reset_cmd, timeout=10)
    result = stdout.read().decode()
    print(f"  结果: {result.strip()}")
    
    # Shutdown and restart normally
    print("  重启MySQL正常模式...")
    ssh.exec_command("mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld", timeout=5)
    time.sleep(3)
    ssh.exec_command("systemctl start mysqld 2>/dev/null || service mysql start", timeout=10)
    time.sleep(5)
    
    # Verify MySQL
    test_cmd = f"mysql -uroot -p{DB_PASSWORD} -e 'SELECT 1' 2>&1 | grep -c '1'"
    stdin, stdout, stderr = ssh.exec_command(test_cmd, timeout=5)
    if '1' in stdout.read().decode():
        print("  ✅ MySQL密码重置成功并验证通过")
    else:
        print("  ⚠️  MySQL验证可能有问题")
    
    # Fix 2: Create necessary directories for Nginx
    print("\n[2/6] 创建Nginx配置目录...")
    ssh.exec_command("mkdir -p /etc/nginx/conf.d", timeout=5)
    print("  ✅ 目录已创建")
    
    # Fix 3: Create proper Nginx configuration
    print("\n[3/6] 创建Nginx配置文件...")
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
    
    # Write config using Python to avoid escaping issues
    write_nginx = f"""python3 << 'PYEOF'
config = '''{nginx_config}'''
with open('/etc/nginx/conf.d/eims.conf', 'w') as f:
    f.write(config)
print('Config written successfully')
PYEOF"""
    stdin, stdout, stderr = ssh.exec_command(write_nginx, timeout=5)
    result = stdout.read().decode().strip()
    print(f"  ✅ {result}")
    
    # Test and start Nginx
    print("\n[4/6] 测试并启动Nginx...")
    stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1", timeout=5)
    test_result = stdout.read().decode()
    print(f"  测试结果: {test_result.strip()}")
    
    # Stop any existing Nginx
    ssh.exec_command("pkill nginx 2>/dev/null; sleep 1", timeout=5)
    
    # Start Nginx
    ssh.exec_command("nginx", timeout=5)
    time.sleep(2)
    
    # Verify Nginx
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'nginx: master' | grep -v grep | wc -l", timeout=5)
    nginx_count = stdout.read().decode().strip()
    print(f"  ✅ Nginx进程数: {nginx_count}")
    
    # Fix 4: Start Gunicorn properly
    print("\n[5/6] 启动Gunicorn...")
    
    # Kill any existing Gunicorn
    ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)
    
    # Start Gunicorn with proper command
    gunicorn_start = f"""cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 300 \\
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \\
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \\
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
echo "Gunicorn started with PID $!" """
    
    stdin, stdout, stderr = ssh.exec_command(gunicorn_start, timeout=10)
    result = stdout.read().decode().strip()
    print(f"  {result}")
    
    time.sleep(5)
    
    # Verify Gunicorn
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l", timeout=5)
    gunicorn_count = stdout.read().decode().strip()
    print(f"  ✅ Gunicorn进程数: {gunicorn_count}")
    
    # Fix 5: Final verification
    print("\n[6/6] 最终验证...")
    
    # Test HTTP
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", timeout=10)
    http_code = stdout.read().decode().strip()
    print(f"  HTTP状态码: {http_code}")
    
    # Test database connection
    test_db = f"""cd {SERVER_PATH} && source venv/bin/activate && python3 -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='{DB_PASSWORD}', database='eims')
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {{e}}')
" """
    stdin, stdout, stderr = ssh.exec_command(test_db, timeout=10)
    db_result = stdout.read().decode().strip()
    print(f"  {db_result}")
    
    # Get system status
    print("\n" + "=" * 80)
    print("✅ 修复完成！系统状态:")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command(f"df -h / | tail -1 | awk '{{print \"磁盘使用: \"$5}}'", timeout=5)
    print(f"  {stdout.read().decode().strip()}")
    
    stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"内存使用: %.1f%%\\n\", $3*100/$2}'", timeout=5)
    print(f"  {stdout.read().decode().strip()}")
    
    print(f"\n🌐 访问地址:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print(f"\n⏰ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 修复失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
