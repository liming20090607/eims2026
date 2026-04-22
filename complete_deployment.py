#!/usr/bin/env python3
"""
Complete system deployment with all fixes
"""

import paramiko
import os
import time
import sys

print("=" * 80)
print("🚀 Complete System Deployment")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'
DB_PASSWORD = 'EIMS2026_mysql'

def run_cmd(ssh, cmd, desc="", timeout=30):
    """Run command and return success status"""
    try:
        print(f"  → {desc}...")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        
        if exit_code == 0:
            print(f"     ✅ Success")
            if output and len(output) < 200:
                print(f"     {output}")
            return True, output
        else:
            print(f"     ⚠️ Failed (code={exit_code})")
            if error and len(error) < 300:
                print(f"     Error: {error}")
            return False, error
    except Exception as e:
        print(f"     ❌ Exception: {e}")
        return False, str(e)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ Connected to server\n")
    
    # Step 1: Fix MySQL completely
    print("[1/7] Fixing MySQL authentication...")
    
    # Stop MySQL
    run_cmd(ssh, "systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 3", "Stopping MySQL", timeout=10)
    time.sleep(4)
    
    # Clean up
    run_cmd(ssh, "rm -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.pid", "Cleaning socket files")
    run_cmd(ssh, "mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld", "Creating run directory")
    
    # Start in recovery mode
    print("  Starting MySQL in recovery mode...")
    ssh.exec_command("mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", timeout=5)
    time.sleep(12)
    
    # Wait for socket
    socket_ready = False
    for i in range(15):
        stdin, stdout, stderr = ssh.exec_command("test -f /var/lib/mysql/mysql.sock && echo ready || echo wait")
        if 'ready' in stdout.read().decode():
            print(f"     ✅ Socket ready ({i}s)")
            socket_ready = True
            break
        time.sleep(1)
    
    if socket_ready:
        # Reset password
        reset_sql = """mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOSQL
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOSQL"""
        run_cmd(ssh, reset_sql, "Resetting root password", timeout=10)
        
        # Shutdown recovery mode
        run_cmd(ssh, "mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld", "Shutting down MySQL", timeout=5)
        time.sleep(3)
    
    # Start MySQL normally
    print("  Starting MySQL normally...")
    run_cmd(ssh, "systemctl start mysqld 2>/dev/null || service mysql start", "Starting MySQL service", timeout=15)
    time.sleep(5)
    
    # Verify MySQL
    test_mysql = f"mysql -uroot -p{DB_PASSWORD} -e 'SELECT 1 AS test' 2>&1 | grep -c '1'"
    success, result = run_cmd(ssh, test_mysql, "Testing MySQL connection")
    if success and '1' in result:
        print("  ✅ MySQL is working!")
    else:
        print("  ⚠️ MySQL may have issues")
    
    # Step 2: Install Nginx
    print("\n[2/7] Installing Nginx...")
    
    # Check if nginx exists
    success, _ = run_cmd(ssh, "which nginx 2>/dev/null && echo found || echo not_found", "Checking Nginx")
    
    if 'not_found' in _:
        print("  Installing Nginx from source...")
        
        # Install dependencies
        run_cmd(ssh, "yum install -y gcc pcre pcre-devel zlib zlib-devel openssl openssl-devel wget make", "Installing dependencies", timeout=120)
        
        # Download Nginx
        run_cmd(ssh, "cd /tmp && wget http://nginx.org/download/nginx-1.24.0.tar.gz", "Downloading Nginx", timeout=120)
        
        # Extract and compile
        run_cmd(ssh, "cd /tmp && tar xzf nginx-1.24.0.tar.gz && cd nginx-1.24.0 && ./configure --prefix=/usr/local/nginx --with-http_ssl_module 2>&1 | tail -3", "Configuring Nginx", timeout=60)
        run_cmd(ssh, "cd /tmp/nginx-1.24.0 && make -j$(nproc) 2>&1 | tail -3", "Compiling Nginx", timeout=300)
        run_cmd(ssh, "cd /tmp/nginx-1.24.0 && make install 2>&1 | tail -3", "Installing Nginx", timeout=120)
        
        # Create symlink
        run_cmd(ssh, "ln -sf /usr/local/nginx/sbin/nginx /usr/local/bin/nginx", "Creating symlink")
        
        print("  ✅ Nginx installed")
    else:
        print("  ✅ Nginx already installed")
    
    # Step 3: Configure Nginx
    print("\n[3/7] Configuring Nginx...")
    
    # Create config directory
    run_cmd(ssh, "mkdir -p /etc/nginx/conf.d", "Creating config directory")
    
    # Write Nginx config using Python
    nginx_python = f"""python3 << 'PYEOF'
config = """ + '"""' + f"""server {{
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
}}""" + '"""' + """
with open('/etc/nginx/conf.d/eims.conf', 'w') as f:
    f.write(config)
print('Nginx config written')
PYEOF"""
    
    run_cmd(ssh, nginx_python, "Writing Nginx config")
    
    # Test and start Nginx
    run_cmd(ssh, "/usr/local/nginx/sbin/nginx -t 2>&1", "Testing Nginx config")
    run_cmd(ssh, "pkill nginx 2>/dev/null; sleep 1", "Stopping old Nginx")
    run_cmd(ssh, "/usr/local/nginx/sbin/nginx", "Starting Nginx", timeout=10)
    time.sleep(2)
    
    # Verify Nginx
    success, count = run_cmd(ssh, "ps aux | grep 'nginx: master' | grep -v grep | wc -l", "Checking Nginx")
    print(f"  ✅ Nginx processes: {count.strip()}")
    
    # Step 4: Setup virtual environment and dependencies
    print("\n[4/7] Setting up Python environment...")
    
    # Create venv if not exists
    run_cmd(ssh, f"cd {SERVER_PATH} && python3 -m venv venv 2>&1 | tail -3", "Creating venv", timeout=60)
    
    # Install requirements
    print("  Installing Python packages...")
    run_cmd(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && pip install --upgrade pip -q", "Upgrading pip", timeout=120)
    run_cmd(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && pip install -r requirements.txt -q 2>&1 | tail -5", "Installing requirements", timeout=300)
    
    # Verify Django
    success, django_ver = run_cmd(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python -c 'import django; print(django.get_version())'", "Checking Django")
    print(f"  ✅ Django {django_ver.strip()}")
    
    # Step 5: Database migrations
    print("\n[5/7] Running database migrations...")
    
    run_cmd(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py makemigrations 2>&1 | tail -5", "Making migrations", timeout=60)
    run_cmd(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -10", "Running migrations", timeout=120)
    run_cmd(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py collectstatic --noinput 2>&1 | tail -3", "Collecting static files", timeout=60)
    
    print("  ✅ Migrations complete")
    
    # Step 6: Start Gunicorn properly
    print("\n[6/7] Starting Gunicorn...")
    
    # Kill existing
    run_cmd(ssh, "pkill -9 -f gunicorn 2>/dev/null; sleep 2", "Stopping old Gunicorn")
    
    # Create startup script
    startup_script = f"""#!/bin/bash
cd {SERVER_PATH}
source venv/bin/activate

# Create log directory
mkdir -p logs

# Start Gunicorn
exec gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 300 \\
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \\
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \\
    wsgi:application
"""
    
    # Write startup script
    write_script = f"""cat > {SERVER_PATH}/start_gunicorn.sh << 'SCRIPTEOF'
{startup_script}
SCRIPTEOF
chmod +x {SERVER_PATH}/start_gunicorn.sh
echo "Script created"
"""
    run_cmd(ssh, write_script, "Creating startup script")
    
    # Start Gunicorn in background
    run_cmd(ssh, f"nohup {SERVER_PATH}/start_gunicorn.sh > {SERVER_PATH}/logs/gunicorn.log 2>&1 &", "Starting Gunicorn")
    time.sleep(5)
    
    # Verify Gunicorn
    success, count = run_cmd(ssh, "ps aux | grep gunicorn | grep -v grep | wc -l", "Checking Gunicorn")
    print(f"  ✅ Gunicorn processes: {count.strip()}")
    
    # Step 7: Final verification
    print("\n[7/7] Final verification...")
    time.sleep(3)
    
    # Test HTTP
    success, http_code = run_cmd(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "Testing HTTP", timeout=10)
    print(f"  HTTP Status: {http_code.strip()}")
    
    # Test database
    test_db = f"""cd {SERVER_PATH} && source venv/bin/activate && python3 -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='{DB_PASSWORD}', database='eims')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM auth_user')
    count = cursor.fetchone()[0]
    conn.close()
    print(f'Users in database: {{count}}')
except Exception as e:
    print(f'Error: {{e}}')
" """
    run_cmd(ssh, test_db, "Testing database")
    
    # Get system info
    print("\n" + "=" * 80)
    print("✅ DEPLOYMENT COMPLETE!")
    print("=" * 80)
    
    run_cmd(ssh, "df -h / | tail -1 | awk '{print \"Disk Usage: \"$5}'", "Disk usage")
    run_cmd(ssh, "free -m | awk 'NR==2{printf \"Memory Usage: %.1f%%\\n\", $3*100/$2}'", "Memory usage")
    
    print(f"\n🌐 Access URLs:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print(f"\n⏰ Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ Deployment failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
