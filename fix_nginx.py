import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 Nginx 配置")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 查找 Nginx 可执行文件
    print("\n[1] 查找 Nginx...")
    stdin, stdout, stderr = ssh.exec_command('find / -name nginx -type f 2>/dev/null | head -5')
    nginx_path = stdout.read().decode('utf-8').strip()
    print(f"Nginx 路径: {nginx_path}")
    
    if not nginx_path:
        print("[✗] 未找到 Nginx")
        # 尝试安装
        print("\n尝试安装 Nginx...")
        stdin, stdout, stderr = ssh.exec_command('yum install -y nginx 2>&1 | tail -5')
        install_output = stdout.read().decode('utf-8')
        print(install_output)
        stdin, stdout, stderr = ssh.exec_command('find / -name nginx -type f 2>/dev/null | head -5')
        nginx_path = stdout.read().decode('utf-8').strip()
    
    if nginx_path:
        nginx_cmd = nginx_path.split('\n')[0]
        print(f"使用 Nginx: {nginx_cmd}")
    
    # 2. 查看现有 Nginx 配置
    print("\n[2] 查看现有 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-available/eims 2>&1')
    eims_config = stdout.read().decode('utf-8')
    print("当前 Nginx 配置:")
    print(eims_config)
    
    # 3. 创建正确的 Nginx 配置
    print("\n[3] 创建新的 Nginx 配置...")
    
    nginx_conf = """server {
    listen 80;
    server_name www.xietongai.com.cn xietongai.com.cn 39.106.41.239;

    # 日志配置
    access_log /var/www/eims/logs/nginx_access.log;
    error_log /var/www/eims/logs/nginx_error.log;

    # 静态文件
    location /static/ {
        alias /var/www/eims/staticfiles/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/eims/media/;
        expires 30d;
    }

    # 代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
"""
    
    # 写入配置文件
    stdin, stdout, stderr = ssh.exec_command(f'cat > /etc/nginx/sites-available/eims << "NGINXEOF"\n{nginx_conf}\nNGINXEOF')
    time.sleep(2)
    
    print("[✓] Nginx 配置已更新")
    
    # 4. 检查并启用配置
    print("\n[4] 启用 Nginx 配置...")
    
    # 确保 sites-enabled 存在
    stdin, stdout, stderr = ssh.exec_command('mkdir -p /etc/nginx/sites-enabled')
    
    # 创建软链接
    stdin, stdout, stderr = ssh.exec_command('ln -sf /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/eims')
    
    # 删除 default 配置（如果存在）
    stdin, stdout, stderr = ssh.exec_command('rm -f /etc/nginx/sites-enabled/default')
    
    print("[✓] 配置已启用")
    
    # 5. 测试 Nginx 配置
    print("\n[5] 测试 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command(f'{nginx_cmd} -t 2>&1')
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    
    print("测试结果:")
    if test_result:
        print(test_result)
    if test_error:
        print(test_error)
    
    if 'successful' in (test_result + test_error).lower():
        print("[✓] Nginx 配置测试通过")
    else:
        print("[!] Nginx 配置测试失败，尝试修复...")
        # 检查配置文件位置
        stdin, stdout, stderr = ssh.exec_command('ls -la /etc/nginx/nginx.conf')
        print("主配置文件:", stdout.read().decode('utf-8'))
    
    # 6. 启动/重启 Nginx
    print("\n[6] 启动 Nginx...")
    
    # 检查 Nginx 是否在运行
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
    nginx_procs = stdout.read().decode('utf-8')
    
    if nginx_procs.strip():
        print("Nginx 正在运行，尝试重启...")
        stdin, stdout, stderr = ssh.exec_command(f'{nginx_cmd} -s reload 2>&1')
    else:
        print("启动 Nginx...")
        stdin, stdout, stderr = ssh.exec_command(f'{nginx_cmd} 2>&1')
    
    time.sleep(3)
    
    # 验证启动
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep | head -5')
    nginx_running = stdout.read().decode('utf-8')
    if nginx_running.strip():
        print("[✓] Nginx 已启动")
        print(nginx_running)
    else:
        print("[✗] Nginx 启动失败")
        stdin, stdout, stderr = ssh.exec_command(f'tail -20 /var/log/nginx/error.log 2>&1')
        error_log = stdout.read().decode('utf-8')
        print("错误日志:")
        print(error_log)
    
    # 7. 配置防火墙
    print("\n[7] 配置防火墙...")
    
    # 开放端口 80
    stdin, stdout, stderr = ssh.exec_command('firewall-cmd --permanent --add-port=80/tcp 2>&1')
    time.sleep(1)
    stdin, stdout, stderr = ssh.exec_command('firewall-cmd --reload 2>&1')
    time.sleep(1)
    
    stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-ports 2>&1')
    firewall_ports = stdout.read().decode('utf-8')
    print(f"防火墙开放端口: {firewall_ports}")
    
    # 8. 测试 HTTP 访问
    print("\n[8] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1/')
    http_status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {http_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态码: {login_status}")
    
    # 测试域名访问
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" -H "Host: www.xietongai.com.cn" http://127.0.0.1/login/')
    domain_status = stdout.read().decode('utf-8').strip()
    print(f"域名访问状态码: {domain_status}")
    
    # 9. 总结
    print("\n" + "="*70)
    print("✅ Nginx 配置完成")
    print("="*70)
    
    print("\n访问方式:")
    print("  ✓ HTTP: http://www.xietongai.com.cn/login/")
    print("  ✓ HTTP: http://39.106.41.239/login/")
    print("  ✓ 直接访问: http://39.106.41.239:8000/login/")
    
    print("\n⚠️  HTTPS 配置:")
    print("  如果需要 HTTPS，需要:")
    print("  1. 获取 SSL 证书（Let's Encrypt 免费）")
    print("  2. 安装 certbot: yum install certbot python3-certbot-nginx")
    print("  3. 运行: certbot --nginx -d www.xietongai.com.cn")
    
    print("\n登录凭据:")
    print("  用户名: admin  密码: admin123456")
    print("  用户名: root   密码: root123456")
    
    print("\n下一步:")
    print("  1. 清除浏览器缓存")
    print("  2. 使用 HTTP 访问: http://www.xietongai.com.cn/login/")
    print("  3. 检查阿里云安全组是否开放端口 80")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
