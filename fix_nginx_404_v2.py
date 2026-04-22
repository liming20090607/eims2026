import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 Nginx 404 问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前 Nginx 主配置
    print("\n[1] 检查 Nginx 主配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /usr/local/nginx/conf/nginx.conf')
    main_config = stdout.read().decode('utf-8')
    print("主配置文件 (前50行):")
    print('\n'.join(main_config.split('\n')[:50]))
    
    # 2. 检查是否已经 include sites-enabled
    has_include = 'sites-enabled' in main_config
    print(f"\n是否包含 sites-enabled: {has_include}")
    
    # 3. 如果未包含，添加 include 指令
    if not has_include:
        print("\n[3] 添加 sites-enabled include...")
        
        # 备份
        stdin, stdout, stderr = ssh.exec_command('cp /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.backup')
        
        # 使用 sed 在 http 块结束前添加 include
        add_include_cmd = '''sed -i '/^}$/i \\    # 包含站点配置\\n    include /etc/nginx/sites-enabled/*;' /usr/local/nginx/conf/nginx.conf'''
        stdin, stdout, stderr = ssh.exec_command(add_include_cmd)
        time.sleep(2)
        print("[✓] 已添加 include 指令")
    else:
        print("[✓] sites-enabled 已经包含")
    
    # 4. 重新创建 EIMS Nginx 配置
    print("\n[4] 重新创建 EIMS Nginx 配置...")
    
    nginx_conf = """server {
    listen 80;
    server_name www.xietongai.com.cn xietongai.com.cn 39.106.41.239 localhost;

    access_log /var/www/eims/logs/nginx_access.log;
    error_log /var/www/eims/logs/nginx_error.log;

    charset utf-8;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/eims/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/eims/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /etc/nginx/sites-available/eims << "NGINXEOF"\n{nginx_conf}\nNGINXEOF')
    time.sleep(2)
    print("[✓] Nginx 配置已更新")
    
    # 5. 确保符号链接正确
    print("\n[5] 确保配置启用...")
    stdin, stdout, stderr = ssh.exec_command('rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/eims')
    stdin, stdout, stderr = ssh.exec_command('ls -la /etc/nginx/sites-enabled/')
    links = stdout.read().decode('utf-8')
    print("sites-enabled 内容:")
    print(links)
    
    # 6. 测试 Nginx 配置
    print("\n[6] 测试 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -t 2>&1')
    test_result = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
    print("测试结果:")
    print(test_result)
    
    if 'successful' in test_result.lower():
        print("[✓] 配置测试通过")
    else:
        print("[✗] 配置测试失败")
        print("\n查看当前 nginx.conf:")
        stdin, stdout, stderr = ssh.exec_command('tail -20 /usr/local/nginx/conf/nginx.conf')
        print(stdout.read().decode('utf-8'))
    
    # 7. 重启 Nginx
    print("\n[7] 重启 Nginx...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -s stop 2>&1 || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx 2>&1')
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
    nginx_procs = stdout.read().decode('utf-8')
    if nginx_procs.strip():
        print("[✓] Nginx 已启动")
        print(nginx_procs)
    
    # 8. 测试访问
    print("\n[8] 测试访问...")
    time.sleep(2)
    
    test_urls = [
        ('/', '主页'),
        ('/login/', '登录页面'),
        ('/admin/', '管理后台'),
    ]
    
    for url, desc in test_urls:
        # 测试 Nginx (端口 80)
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1{url}')
        nginx_status = stdout.read().decode('utf-8').strip()
        
        # 测试直接 Gunicorn (端口 8000)
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8000{url}')
        gunicorn_status = stdout.read().decode('utf-8').strip()
        
        match = "✓" if nginx_status == gunicorn_status else "✗"
        print(f"  {match} {desc:15s} Nginx:{nginx_status:6s} Gunicorn:{gunicorn_status}")
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    print("\n访问方式:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239/login/")
    print("\n登录凭据:")
    print("  用户名: admin  密码: admin123456")
    print("  用户名: root   密码: root123456")
    print("\n注意:")
    print("  - 请使用 HTTP，不要使用 HTTPS")
    print("  - 如果浏览器自动跳转 HTTPS，请手动输入 HTTP 地址")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
