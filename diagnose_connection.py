import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("诊断连接问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查 Gunicorn 进程
    print("\n[1] 检查 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_procs = stdout.read().decode('utf-8')
    
    if gunicorn_procs.strip():
        print("[✓] Gunicorn 正在运行")
        proc_count = len([line for line in gunicorn_procs.strip().split('\n') if line])
        print(f"进程数: {proc_count}")
    else:
        print("[✗] Gunicorn 未运行，需要重启")
        
        # 启动 Gunicorn
        print("\n启动 Gunicorn...")
        start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(start_cmd)
        time.sleep(8)
        
        # 验证启动
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
        count = stdout.read().decode('utf-8').strip()
        print(f"Gunicorn 进程数: {count}")
    
    # 2. 检查端口监听
    print("\n[2] 检查端口监听...")
    stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep 8000')
    port_info = stdout.read().decode('utf-8')
    
    if '8000' in port_info:
        print("[✓] 端口 8000 正在监听")
        print(port_info)
    else:
        print("[✗] 端口 8000 未监听")
    
    # 3. 检查防火墙
    print("\n[3] 检查防火墙状态...")
    stdin, stdout, stderr = ssh.exec_command('systemctl status firewalld 2>/dev/null | head -5 || iptables -L -n | head -10')
    firewall_info = stdout.read().decode('utf-8')
    print("防火墙信息:")
    print(firewall_info[:500])
    
    # 4. 测试本地访问
    print("\n[4] 测试本地访问...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:8000/')
    http_status = stdout.read().decode('utf-8').strip()
    print(f"本地 HTTP 状态: {http_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:8000/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面 HTTP 状态: {login_status}")
    
    # 5. 检查是否有 Nginx 配置
    print("\n[5] 检查 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 | head -5')
    nginx_test = stdout.read().decode('utf-8')
    
    if 'nginx' in nginx_test.lower() or 'successful' in nginx_test.lower():
        print("Nginx 配置存在")
        print(nginx_test)
        
        # 检查 Nginx 配置
        stdin, stdout, stderr = ssh.exec_command('ls -la /etc/nginx/conf.d/ /etc/nginx/sites-enabled/ 2>/dev/null')
        nginx_conf = stdout.read().decode('utf-8')
        print("\nNginx 配置文件:")
        print(nginx_conf)
    else:
        print("未找到 Nginx 配置")
    
    # 6. 检查 DNS 解析
    print("\n[6] 检查域名解析...")
    stdin, stdout, stderr = ssh.exec_command('nslookup www.xietongai.com.cn 2>&1 | grep Address | tail -1')
    dns_result = stdout.read().decode('utf-8').strip()
    print(f"域名解析: {dns_result}")
    
    # 7. 检查云服务器安全组（提示）
    print("\n[7] 检查云服务器配置...")
    print("请确认阿里云安全组已开放以下端口:")
    print("  - 端口 80 (HTTP)")
    print("  - 端口 443 (HTTPS)")
    print("  - 端口 8000 (应用端口)")
    
    # 8. 提供访问建议
    print("\n" + "="*70)
    print("✅ 诊断完成")
    print("="*70)
    
    if login_status == '200':
        print("\n服务运行正常！")
        print("\n访问方式:")
        print("  ✓ 直接访问: http://39.106.41.239:8000/login/")
        print("  ✓ 域名访问: http://www.xietongai.com.cn/login/")
        print("\n⚠️  注意:")
        print("  - 请使用 HTTP 而不是 HTTPS")
        print("  - 如果您需要 HTTPS，需要:")
        print("    1. 安装 SSL 证书")
        print("    2. 配置 Nginx 反向代理")
        print("    3. 或使用云服务商的负载均衡+SSL")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n服务存在问题，请检查:")
        print(f"  - HTTP 状态: {http_status}")
        print(f"  - 登录页面状态: {login_status}")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
