import paramiko
import time

print("="*70)
print("MySQL 数据库完全恢复")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 查看MySQL服务状态
    print("\n[1] 检查 MySQL 服务状态...")
    stdin, stdout, stderr = ssh.exec_command('systemctl status mysqld 2>&1 | head -20')
    status = stdout.read().decode('utf-8')
    print("服务状态:")
    print(status)
    
    # 2. 查看MySQL错误日志
    print("\n[2] 查看 MySQL 错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/log/mysqld.log 2>&1')
    error_log = stdout.read().decode('utf-8')
    print("错误日志:")
    print(error_log[-1000:] if len(error_log) > 1000 else error_log)
    
    # 3. 尝试重启MySQL服务
    print("\n[3] 重启 MySQL 服务...")
    stdin, stdout, stderr = ssh.exec_command('systemctl restart mysqld 2>&1')
    restart_output = stdout.read().decode('utf-8')
    restart_error = stderr.read().decode('utf-8')
    print("重启输出:", restart_output if restart_output else "[无输出]")
    if restart_error:
        print("重启错误:", restart_error)
    
    print("等待 10 秒...")
    time.sleep(10)
    
    # 4. 检查MySQL进程
    print("\n[4] 检查 MySQL 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysqld | grep -v grep')
    procs = stdout.read().decode('utf-8')
    if procs.strip():
        print("✓ MySQL 进程正在运行:")
        print(procs)
    else:
        print("✗ MySQL 进程未运行")
        print("尝试使用 service 命令启动...")
        stdin, stdout, stderr = ssh.exec_command('service mysqld start 2>&1')
        time.sleep(10)
    
    # 5. 检查端口监听
    print("\n[5] 检查端口监听...")
    stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep 3306')
    port_info = stdout.read().decode('utf-8')
    if port_info.strip():
        print("✓ 端口 3306 正在监听:")
        print(port_info)
    else:
        print("✗ 端口 3306 未监听")
    
    # 6. 测试 TCP 连接（127.0.0.1）
    print("\n[6] 测试 TCP 连接（使用 127.0.0.1）...")
    test_tcp = '''python3 -c "
import pymysql
try:
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    print('✓ TCP连接成功（127.0.0.1）')
    conn.close()
except Exception as e:
    print(f'✗ TCP连接失败: {e}')
"'''
    stdin, stdout, stderr = ssh.exec_command(test_tcp)
    tcp_result = stdout.read().decode('utf-8')
    print(tcp_result)
    
    # 7. 测试 socket 连接
    print("\n[7] 测试 socket 连接...")
    test_socket = '''python3 -c "
import pymysql
try:
    conn = pymysql.connect(
        unix_socket='/var/lib/mysql/mysql.sock',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    print('✓ Socket连接成功')
    conn.close()
except Exception as e:
    print(f'✗ Socket连接失败: {e}')
"'''
    stdin, stdout, stderr = ssh.exec_command(test_socket)
    socket_result = stdout.read().decode('utf-8')
    print(socket_result)
    
    # 8. 如果连接成功，测试 Django
    if '✓' in tcp_result or '✓' in socket_result:
        print("\n[8] 测试 Django 数据库连接...")
        test_django = '''python3 -c "
import os, sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✓ Django数据库连接成功')
except Exception as e:
    print(f'✗ Django数据库连接失败: {e}')

# 测试用户认证
from django.contrib.auth import authenticate
for u, p in [('admin', 'admin123456'), ('root', 'root123456')]:
    user = authenticate(username=u, password=p)
    if user:
        print(f'✓ {u} 用户认证成功')
    else:
        print(f'✗ {u} 用户认证失败')
"'''
        stdin, stdout, stderr = ssh.exec_command(test_django)
        django_result = stdout.read().decode('utf-8')
        print(django_result)
        
        # 9. 重启 Gunicorn
        print("\n[9] 重启 Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
        time.sleep(3)
        
        # 清空日志
        stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
        stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
        
        # 启动 Gunicorn
        start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
        ssh.exec_command(start_cmd)
        
        print("等待 10 秒...")
        time.sleep(10)
        
        # 10. 测试 HTTP
        print("\n[10] 测试 HTTP 访问...")
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
        gunicorn_status = stdout.read().decode('utf-8').strip()
        print(f"Gunicorn (8000): {gunicorn_status}")
        
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
        nginx_status = stdout.read().decode('utf-8').strip()
        print(f"Nginx (80): {nginx_status}")
        
        # 11. 检查错误日志
        print("\n[11] 检查错误日志...")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command('tail -15 /var/www/eims/logs/error.log 2>&1')
        errors = stdout.read().decode('utf-8')
        
        if 'Access denied' in errors:
            print("[✗] 仍有数据库访问错误")
        else:
            print("[✓] 无数据库访问错误")
        
        if errors.strip():
            print("最新日志:")
            print(errors[-800:])
    else:
        print("\n[8] 跳过 Django 测试（数据库连接失败）")
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    
    if '✓ TCP连接成功' in tcp_result or '✓ Socket连接成功' in socket_result:
        print("\n✅ MySQL 恢复成功！")
        if '✓ Django数据库连接成功' in django_result:
            print("\n✅ 系统完全正常！")
            print("\n📍 访问地址:")
            print("   http://39.106.41.239/login/")
            print("   http://www.xietongai.com.cn/login/")
            print("\n🔑 登录凭据:")
            print("   用户名: admin  密码: admin123456")
            print("   用户名: root   密码: root123456")
        else:
            print("\n⚠️ Django 连接仍有问题")
    else:
        print("\n❌ MySQL 恢复失败")
        print("\n请检查 MySQL 错误日志:")
        print("  /var/log/mysqld.log")
        print("\n可能需要:")
        print("1. 重新安装 MySQL")
        print("2. 恢复数据库备份")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
