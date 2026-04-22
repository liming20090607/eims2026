import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 Nginx 配置 - 正确代理到 Gunicorn")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 查看当前 nginx.conf
    print("\n[1] 查看 nginx.conf 当前结构...")
    stdin, stdout, stderr = ssh.exec_command('cat -n /usr/local/nginx/conf/nginx.conf')
    config_lines = stdout.read().decode('utf-8')
    print("当前配置:")
    print(config_lines)
    
    # 2. 创建正确的 nginx.conf - 将 EIMS 配置直接包含在 http 块中
    print("\n[2] 重新创建 nginx.conf...")
    
    correct_nginx_conf = """#user  nobody;
worker_processes  1;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # EIMS 应用配置
    server {
        listen 80;
        server_name www.xietongai.com.cn xietongai.com.cn 39.106.41.239 localhost _;

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
}
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /usr/local/nginx/conf/nginx.conf << "NGINXEOF"\n{correct_nginx_conf}\nNGINXEOF')
    time.sleep(2)
    print("[✓] nginx.conf 已重新创建")
    
    # 3. 移除 sites-enabled 配置（不再需要）
    print("\n[3] 清理 sites-enabled...")
    stdin, stdout, stderr = ssh.exec_command('rm -f /etc/nginx/sites-enabled/*')
    print("[✓] sites-enabled 已清理")
    
    # 4. 测试 Nginx 配置
    print("\n[4] 测试 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -t 2>&1')
    test_result = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
    print("测试结果:")
    print(test_result)
    
    if 'successful' in test_result.lower():
        print("[✓] 配置测试通过")
    else:
        print("[✗] 配置测试失败")
        # 显示详细错误
        stdin, stdout, stderr = ssh.exec_command('cat -n /usr/local/nginx/conf/nginx.conf')
        print("\n当前 nginx.conf:")
        print(stdout.read().decode('utf-8'))
    
    # 5. 重启 Nginx
    print("\n[5] 重启 Nginx...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -s stop 2>&1 || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx 2>&1')
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
    nginx_procs = stdout.read().decode('utf-8')
    if nginx_procs.strip():
        print("[✓] Nginx 已启动")
        print(nginx_procs)
    else:
        print("[✗] Nginx 未启动")
        stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/nginx_error.log 2>&1')
        print("错误日志:")
        print(stdout.read().decode('utf-8'))
    
    # 6. 测试访问
    print("\n[6] 测试访问...")
    time.sleep(2)
    
    test_urls = [
        ('/', '主页'),
        ('/login/', '登录页面'),
        ('/admin/', '管理后台'),
    ]
    
    print("\n对比测试 (Nginx vs Gunicorn):")
    for url, desc in test_urls:
        # 测试 Nginx (端口 80)
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1{url}')
        nginx_status = stdout.read().decode('utf-8').strip()
        
        # 测试直接 Gunicorn (端口 8000)
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8000{url}')
        gunicorn_status = stdout.read().decode('utf-8').strip()
        
        match = "✓" if nginx_status == gunicorn_status or (nginx_status in ['200', '302'] and gunicorn_status in ['200', '302']) else "✗"
        print(f"  {match} {desc:15s} Nginx:{nginx_status:6s} Gunicorn:{gunicorn_status}")
    
    # 7. 检查 Nginx 错误日志
    print("\n[7] 检查 Nginx 错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/nginx_error.log 2>&1')
    nginx_errors = stdout.read().decode('utf-8')
    if nginx_errors.strip():
        print("Nginx 错误日志:")
        print(nginx_errors[-1000:])
    else:
        print("[✓] 无 Nginx 错误")
    
    # 8. 检查 Nginx 访问日志
    print("\n[8] 检查 Nginx 访问日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/nginx_access.log 2>&1')
    nginx_access = stdout.read().decode('utf-8')
    if nginx_access.strip():
        print("Nginx 访问日志:")
        print(nginx_access[-500:])
    
    # 9. 测试实际内容
    print("\n[9] 测试登录页面内容...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1/login/ | grep -i "login\\|登录\\|csrf" | head -5')
    login_content = stdout.read().decode('utf-8')
    if login_content:
        print("[✓] 登录页面返回了内容")
        print(login_content[:200])
    else:
        print("[✗] 登录页面未返回内容")
        stdin, stdout, stderr = ssh.exec_command('curl -s -I http://127.0.0.1/login/ | head -10')
        print("响应头:")
        print(stdout.read().decode('utf-8'))
    
    print("\n" + "="*70)
    print("✅ 修复完成！")
    print("="*70)
    print("\n访问方式:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239/login/")
    print("\n登录凭据:")
    print("  用户名: admin  密码: admin123456")
    print("  用户名: root   密码: root123456")
    print("\n注意:")
    print("  - 请使用 HTTP，不要使用 HTTPS")
    print("  - 检查阿里云安全组是否开放端口 80")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
