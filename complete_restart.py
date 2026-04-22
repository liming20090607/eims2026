import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("完全重启服务器服务")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 强制杀死所有相关进程
    print("\n[1] 强制停止所有服务...")
    
    # Kill by PID from lsof
    stdin, stdout, stderr = ssh.exec_command('lsof -ti:8000 | xargs kill -9 2>/dev/null || true')
    time.sleep(2)
    
    # Kill gunicorn processes
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn || true')
    time.sleep(2)
    
    # Kill nginx
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -s stop 2>/dev/null || true')
    time.sleep(2)
    
    # Verify ports are free
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 2>/dev/null || echo "Port 8000 is free"')
    port_8000 = stdout.read().decode('utf-8').strip()
    print(f"Port 8000: {port_8000}")
    
    stdin, stdout, stderr = ssh.exec_command('lsof -i :80 2>/dev/null || echo "Port 80 is free"')
    port_80 = stdout.read().decode('utf-8').strip()
    print(f"Port 80: {port_80}")
    
    time.sleep(3)
    
    # 2. Clear logs
    print("\n[2] 清空日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    print("[✓] 日志已清空")
    
    # 3. Start Gunicorn
    print("\n[3] 启动 Gunicorn...")
    start_gunicorn = '''cd /var/www/eims && source venv/bin/activate && nohup gunicorn \\
    --bind 0.0.0.0:8000 \\
    --workers 3 \\
    --timeout 120 \\
    --access-logfile /var/www/eims/logs/access.log \\
    --error-logfile /var/www/eims/logs/error.log \\
    --capture-output \\
    wsgi:application &'''
    
    stdin, stdout, stderr = ssh.exec_command(start_gunicorn)
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    # Verify Gunicorn
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_procs = stdout.read().decode('utf-8')
    if gunicorn_procs.strip():
        proc_count = len([line for line in gunicorn_procs.strip().split('\n') if line])
        print(f"[✓] Gunicorn 已启动 (进程数: {proc_count})")
    else:
        print("[✗] Gunicorn 启动失败")
        stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log')
        print("错误日志:")
        print(stdout.read().decode('utf-8'))
    
    # 4. Start Nginx
    print("\n[4] 启动 Nginx...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx')
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
    nginx_procs = stdout.read().decode('utf-8')
    if nginx_procs.strip():
        print("[✓] Nginx 已启动")
    else:
        print("[✗] Nginx 启动失败")
    
    # 5. Test services
    print("\n[5] 测试服务...")
    time.sleep(3)
    
    # Test Gunicorn directly
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    # Test Nginx
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # Test with IP
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://39.106.41.239/login/ 2>/dev/null')
    ip_status = stdout.read().decode('utf-8').strip()
    print(f"IP访问 (80): {ip_status}")
    
    # 6. Check for errors
    print("\n[6] 检查错误...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>/dev/null')
    errors = stdout.read().decode('utf-8')
    
    if errors.strip():
        if 'Access denied' in errors:
            print("[✗] 数据库连接错误")
        elif 'Address already in use' in errors:
            print("[!] 端口占用（旧进程）")
        else:
            print("[✓] 无严重错误")
        print("\n错误日志:")
        print(errors[-1000:])
    else:
        print("[✓] 无错误")
    
    print("\n" + "="*70)
    print("✅ 服务重启完成")
    print("="*70)
    
    if nginx_status == '200' or gunicorn_status == '200':
        print("\n✅ 服务正常运行！")
        print("\n访问地址:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n⚠️ 服务状态异常")
        print(f"  Gunicorn: {gunicorn_status}")
        print(f"  Nginx: {nginx_status}")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
