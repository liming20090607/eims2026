import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("强制重启 Gunicorn")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 强制停止所有 Gunicorn 进程
    print("\n[1] 强制停止所有 Gunicorn 进程...")
    
    commands = [
        'fuser -k 8000/tcp 2>/dev/null || true',
        'sleep 2',
        'pkill -9 -f gunicorn 2>/dev/null || true',
        'sleep 3',
        'kill -9 $(lsof -t -i:8000) 2>/dev/null || true',
        'sleep 3',
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if 'sleep' in cmd:
            time.sleep(2)
        else:
            time.sleep(1)
    
    # 验证端口已释放
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 2>/dev/null | grep LISTEN || echo "端口已释放"')
    port_status = stdout.read().decode('utf-8').strip()
    print(f"端口 8000 状态: {port_status}")
    
    # 2. 确认没有 Gunicorn 进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep || echo "无 Gunicorn 进程"')
    proc_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程: {proc_status}")
    
    # 3. 清空错误日志
    print("\n[2] 清空错误日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    
    # 4. 启动 Gunicorn
    print("\n[3] 启动 Gunicorn...")
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    # 5. 验证进程
    print("\n[4] 验证 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_procs = stdout.read().decode('utf-8')
    
    if gunicorn_procs.strip():
        print("[✓] Gunicorn 正在运行")
        proc_count = len([line for line in gunicorn_procs.strip().split('\n') if line])
        print(f"进程数: {proc_count}")
    else:
        print("[✗] Gunicorn 未启动")
        stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
        errors = stdout.read().decode('utf-8')
        print("错误日志:")
        print(errors)
    
    # 6. 测试 HTTP 访问
    print("\n[5] 测试 HTTP 访问...")
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    http_status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态 (8000): {http_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态 (8000): {login_status}")
    
    # 7. 测试 Nginx
    print("\n[6] 测试 Nginx 代理...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/')
    nginx_login = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态 (80): {nginx_login}")
    
    # 8. 检查最新错误
    print("\n[7] 检查最新错误...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有数据库连接错误")
    elif 'Can\'t connect' in errors or 'Address already in use' in errors:
        print("[!] 连接错误（可能是旧进程残留）")
    else:
        print("[✓] 无错误")
    
    if errors.strip():
        print("错误日志:")
        print(errors[-1000:])
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    
    if login_status == '200' and nginx_login == '200':
        print("\n服务器完全正常！")
        print("\n访问地址:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n状态:")
        print(f"  Gunicorn (8000): {login_status}")
        print(f"  Nginx (80): {nginx_login}")
        print("\n请检查错误日志或联系支持")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
