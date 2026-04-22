import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 Nginx 配置 - 正确添加 include")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 查看当前 nginx.conf 结构
    print("\n[1] 查看 nginx.conf 当前结构...")
    stdin, stdout, stderr = ssh.exec_command('cat -n /usr/local/nginx/conf/nginx.conf')
    config_lines = stdout.read().decode('utf-8')
    print("当前配置:")
    print(config_lines)
    
    # 2. 备份并重新创建 nginx.conf
    print("\n[2] 重新创建正确的 nginx.conf...")
    
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

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

    # 包含站点配置
    include /etc/nginx/sites-enabled/*;
}
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /usr/local/nginx/conf/nginx.conf << "NGINXEOF"\n{correct_nginx_conf}\nNGINXEOF')
    time.sleep(2)
    print("[✓] nginx.conf 已重新创建")
    
    # 3. 确保 EIMS 配置存在
    print("\n[3] 确保 EIMS 配置存在...")
    stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-available/eims')
    eims_conf = stdout.read().decode('utf-8')
    print("EIMS 配置:")
    print(eims_conf)
    
    # 4. 确保符号链接正确
    print("\n[4] 确保符号链接正确...")
    stdin, stdout, stderr = ssh.exec_command('rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/eims')
    stdin, stdout, stderr = ssh.exec_command('ls -la /etc/nginx/sites-enabled/')
    links = stdout.read().decode('utf-8')
    print("sites-enabled 内容:")
    print(links)
    
    # 5. 测试 Nginx 配置
    print("\n[5] 测试 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -t 2>&1')
    test_result = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
    print("测试结果:")
    print(test_result)
    
    if 'successful' in test_result.lower():
        print("[✓] 配置测试通过")
    else:
        print("[✗] 配置测试失败")
        return
    
    # 6. 重启 Nginx
    print("\n[6] 重启 Nginx...")
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
        return
    
    # 7. 测试访问
    print("\n[7] 测试访问...")
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
    print("  - 如果浏览器自动跳转 HTTPS，请手动输入 HTTP 地址")
    print("  - 检查阿里云安全组是否开放端口 80")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
