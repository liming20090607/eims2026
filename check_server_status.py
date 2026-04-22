import paramiko
import time

print("="*70)
print("诊断服务器状态")
print("="*70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("\n[1] 尝试连接服务器...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#', timeout=10)
    print("[✓] 服务器连接成功")
    
    # 2. 检查系统状态
    print("\n[2] 检查系统状态...")
    stdin, stdout, stderr = ssh.exec_command('uptime')
    uptime = stdout.read().decode('utf-8').strip()
    print(f"系统运行时间: {uptime}")
    
    # 3. 检查内存
    print("\n[3] 检查内存使用...")
    stdin, stdout, stderr = ssh.exec_command('free -h')
    memory = stdout.read().decode('utf-8')
    print("内存使用情况:")
    print(memory)
    
    # 4. 检查磁盘
    print("\n[4] 检查磁盘使用...")
    stdin, stdout, stderr = ssh.exec_command('df -h')
    disk = stdout.read().decode('utf-8')
    print("磁盘使用情况:")
    print(disk)
    
    # 5. 检查 Gunicorn
    print("\n[5] 检查 Gunicorn 状态...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_procs = stdout.read().decode('utf-8')
    if gunicorn_procs.strip():
        print("[✓] Gunicorn 正在运行")
        proc_count = len([line for line in gunicorn_procs.strip().split('\n') if line])
        print(f"进程数: {proc_count}")
    else:
        print("[✗] Gunicorn 未运行")
        # 尝试启动
        print("\n尝试启动 Gunicorn...")
        start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(start_cmd)
        time.sleep(5)
        
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
        count = stdout.read().decode('utf-8').strip()
        print(f"Gunicorn 进程数: {count}")
    
    # 6. 检查 Nginx
    print("\n[6] 检查 Nginx 状态...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
    nginx_procs = stdout.read().decode('utf-8')
    if nginx_procs.strip():
        print("[✓] Nginx 正在运行")
        print(nginx_procs)
    else:
        print("[✗] Nginx 未运行")
        # 尝试启动
        print("\n尝试启动 Nginx...")
        stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx 2>&1')
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
        nginx_running = stdout.read().decode('utf-8')
        if nginx_running.strip():
            print("[✓] Nginx 已启动")
    
    # 7. 检查端口监听
    print("\n[7] 检查端口监听...")
    stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep -E "80|443|8000"')
    ports = stdout.read().decode('utf-8')
    print("端口监听情况:")
    print(ports)
    
    # 8. 测试 HTTP 访问
    print("\n[8] 测试 HTTP 访问...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/')
    http_status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态: {http_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态: {login_status}")
    
    # 9. 检查防火墙
    print("\n[9] 检查防火墙...")
    stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-all 2>&1 | head -20')
    firewall = stdout.read().decode('utf-8')
    print("防火墙配置:")
    print(firewall)
    
    # 10. 检查最近的错误
    print("\n[10] 检查最近错误...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    error_log = stdout.read().decode('utf-8')
    if error_log.strip():
        print("最近错误日志:")
        print(error_log[-1500:])
    else:
        print("[✓] 无错误日志")
    
    # 11. 检查系统负载
    print("\n[11] 系统负载...")
    stdin, stdout, stderr = ssh.exec_command('top -bn1 | head -20')
    top_info = stdout.read().decode('utf-8')
    print(top_info)
    
    print("\n" + "="*70)
    print("✅ 诊断完成")
    print("="*70)
    
    if http_status in ['200', '302'] and login_status == '200':
        print("\n服务器运行正常！")
        print("\n如果外部无法访问，请检查:")
        print("1. 阿里云安全组是否开放端口 80、443、8000")
        print("2. 防火墙配置是否正确")
        print("3. DNS 解析是否正确")
    else:
        print("\n服务器存在问题，请检查上述输出")
    
    print("\n访问地址:")
    print("  http://39.106.41.239/login/")
    print("  http://www.xietongai.com.cn/login/")
    print("\n登录凭据:")
    print("  用户名: admin  密码: admin123456")
    print("  用户名: root   密码: root123456")
    
    ssh.close()
    
except paramiko.ssh_exception.NoValidConnectionsError:
    print("\n[✗] 无法连接到服务器")
    print("\n可能原因:")
    print("1. 服务器已关机")
    print("2. 服务器 IP 地址变更")
    print("3. 防火墙阻止了 SSH 连接")
    print("4. 阿里云安全组未开放端口 22")
    print("\n解决方案:")
    print("1. 登录阿里云控制台检查服务器状态")
    print("2. 检查服务器是否正在运行")
    print("3. 查看阿里云控制台的网络配置")
    
except paramiko.ssh_exception.AuthenticationException:
    print("\n[✗] SSH 认证失败")
    print("请检查用户名和密码是否正确")
    
except Exception as e:
    print(f"\n[✗] 发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
