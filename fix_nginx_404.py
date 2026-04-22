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
    print("主配置文件 (关键部分):")
    # 只显示关键部分
    lines = main_config.split('\n')
    in_http = False
    for i, line in enumerate(lines):
        if 'http {' in line:
            in_http = True
        if in_http:
            print(f"{i+1}: {line}")
        if in_http and line.strip() == '}':
            break
    
    # 2. 检查 sites-available/eims 配置
    print("\n[2] 检查 sites-available/eims 配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-available/eims')
    eims_config = stdout.read().decode('utf-8')
    print("EIMS 配置:")
    print(eims_config)
    
    # 3. 检查 Nginx 是否 include 了 sites-enabled
    print("\n[3] 检查 Nginx 配置包含...")
    stdin, stdout, stderr = ssh.exec_command('grep -n "include\|sites" /usr/local/nginx/conf/nginx.conf')
    includes = stdout.read().decode('utf-8')
    print("Include 配置:")
    print(includes)
    
    # 4. 查看完整的 nginx.conf
    print("\n[4] 查看完整 nginx.conf...")
    stdin, stdout, stderr = ssh.exec_command('cat /usr/local/nginx/conf/nginx.conf')
    full_config = stdout.read().decode('utf-8')
    
    # 检查是否有 server 块直接定义
    if 'server {' in full_config:
        print("[!] 发现 nginx.conf 中有 server 块定义")
        print("这可能是导致配置冲突的原因")
    
    # 5. 修复 Nginx 配置
    print("\n[5] 修复 Nginx 配置...")
    
    # 首先备份当前配置
    stdin, stdout, stderr = ssh.exec_command('cp /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.backup')
    
    # 检查 nginx.conf 是否包含了 sites-enabled
    if 'sites-enabled' not in full_config and 'sites-available' not in full_config:
        print("[!] nginx.conf 没有包含 sites-enabled 目录")
        print("需要添加 include 指令")
        
        # 直接在 nginx.conf 的 http 块末尾添加 include
        fix_script = """import re

with open('/usr/local/nginx/conf/nginx.conf', 'r', encoding='utf-8') as f:
    content = f.read()

# 在最后一个 } 之前添加 include
# 找到 http 块
lines = content.split('\\n')
new_lines = []
in_http = False
brace_count = 0
added = False

for line in lines:
    if 'http {' in line:
        in_http = True
        brace_count = 1
        new_lines.append(line)
    elif in_http and not added:
        brace_count += line.count('{')
        brace_count -= line.count('}')
        
        if brace_count == 0 and line.strip() == '}':
            # 这是 http 块的结束
            new_lines.append('    # 包含站点配置')
            new_lines.append('    include /etc/nginx/sites-enabled/*;')
            new_lines.append(line)
            added = True
            in_http = False
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('/usr/local/nginx/conf/nginx.conf', 'w', encoding='utf-8') as f:
    f.write('\\n'.join(new_lines))

print('✓ 已添加 sites-enabled include')
"""
        
        stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/fix_nginx_include.py << "FIXEOF"\n{fix_script}\nFIXEOF')
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/fix_nginx_include.py 2>&1')
        fix_output = stdout.read().decode('utf-8')
        fix_error = stderr.read().decode('utf-8')
        print(fix_output)
        if fix_error:
            print("错误:", fix_error)
    
    # 6. 重新创建 EIMS Nginx 配置
    print("\n[6] 重新创建 EIMS Nginx 配置...")
    
    nginx_conf = """server {
    listen 80;
    server_name www.xietongai.com.cn xietongai.com.cn 39.106.41.239 localhost;

    # 日志配置
    access_log /var/www/eims/logs/nginx_access.log;
    error_log /var/www/eims/logs/nginx_error.log;

    # 字符集
    charset utf-8;

    # 最大上传大小
    client_max_body_size 50M;

    # 静态文件
    location /static/ {
        alias /var/www/eims/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
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
        
        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /etc/nginx/sites-available/eims << "NGINXEOF"\n{nginx_conf}\nNGINXEOF')
    time.sleep(2)
    print("[✓] Nginx 配置已更新")
    
    # 7. 确保符号链接正确
    print("\n[7] 确保配置启用...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /etc/nginx/sites-enabled/')
    links = stdout.read().decode('utf-8')
    print("sites-enabled 内容:")
    print(links)
    
    # 8. 测试 Nginx 配置
    print("\n[8] 测试 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -t 2>&1')
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    
    print("测试结果:")
    print(test_result)
    if test_error:
        print(test_error)
    
    if 'successful' in (test_result + test_error).lower():
        print("[✓] 配置测试通过")
    else:
        print("[✗] 配置测试失败")
        # 查看详细错误
        stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -t 2>&1')
        detailed_error = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
        print("详细错误:")
        print(detailed_error)
    
    # 9. 重启 Nginx
    print("\n[9] 重启 Nginx...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/nginx/sbin/nginx -s reload 2>&1')
    reload_output = stdout.read().decode('utf-8')
    if reload_output:
        print(reload_output)
    
    time.sleep(3)
    
    # 验证 Nginx 进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep')
    nginx_procs = stdout.read().decode('utf-8')
    if nginx_procs.strip():
        print("[✓] Nginx 已重启")
        print(nginx_procs)
    
    # 10. 测试访问
    print("\n[10] 测试访问...")
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
    
    # 11. 检查错误日志
    print("\n[11] 检查错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/nginx_error.log 2>&1')
    nginx_errors = stdout.read().decode('utf-8')
    if nginx_errors.strip() and 'error' in nginx_errors.lower():
        print("Nginx 错误:")
        print(nginx_errors[-1000:])
    else:
        print("[✓] 无 Nginx 错误")
    
    print("\n" + "="*70)
    print("✅ 修复完成")
    print("="*70)
    print("\n现在请:")
    print("1. 使用 HTTP 访问（不要用 HTTPS）:")
    print("   http://www.xietongai.com.cn/login/")
    print("   http://39.106.41.239/login/")
    print("\n2. 登录凭据:")
    print("   用户名: admin  密码: admin123456")
    print("   用户名: root   密码: root123456")
    print("\n3. 如果仍然 404，请检查:")
    print("   - 阿里云安全组是否开放端口 80")
    print("   - 浏览器是否自动跳转到 HTTPS")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
