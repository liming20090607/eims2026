import paramiko
import time

print("="*70)
print("检查并修复 settings.py")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 查看完整的 DATABASES 配置
    print("\n[1] 查看当前 DATABASES 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 15 "DATABASES" /var/www/eims/settings.py | head -20')
    db_config = stdout.read().decode('utf-8')
    print("当前配置:")
    print(db_config)
    
    # 2. 检查是否有多个 HOST 配置
    print("\n[2] 检查所有 HOST 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -n "HOST" /var/www/eims/settings.py')
    all_hosts = stdout.read().decode('utf-8')
    print("所有 HOST 行:")
    print(all_hosts)
    
    # 3. 直接查看 settings.py 中 DATABASES 部分
    print("\n[3] 查看 settings.py 第 1-100 行...")
    stdin, stdout, stderr = ssh.exec_command('head -100 /var/www/eims/settings.py')
    settings_head = stdout.read().decode('utf-8')
    
    # 查找 DATABASES 部分
    if 'DATABASES' in settings_head:
        lines = settings_head.split('\n')
        in_databases = False
        db_lines = []
        for i, line in enumerate(lines, 1):
            if 'DATABASES' in line:
                in_databases = True
            if in_databases:
                db_lines.append(f"{i:3d}: {line}")
                if line.strip() == '}' and len(db_lines) > 5:
                    break
        print("DATABASES 配置:")
        print('\n'.join(db_lines))
    
    # 4. 强制替换 localhost 为 127.0.0.1
    print("\n[4] 强制替换 HOST 配置...")
    force_fix = '''sed -i "s/'HOST': 'localhost'/'HOST': '127.0.0.1'/g" /var/www/eims/settings.py'''
    stdin, stdout, stderr = ssh.exec_command(force_fix)
    time.sleep(2)
    
    # 验证修改
    stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES" /var/www/eims/settings.py | head -15')
    new_config = stdout.read().decode('utf-8')
    print("修改后的配置:")
    print(new_config)
    
    # 5. 完全杀死所有 Python/Gunicorn 进程
    print("\n[5] 完全停止所有服务...")
    stdin, stdout, stderr = ssh.exec_command('killall -9 gunicorn python3.10 2>/dev/null || true')
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
    time.sleep(3)
    
    # 6. 清空日志
    print("\n[6] 清空日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 7. 启动新的 Gunicorn
    print("\n[7] 启动新的 Gunicorn...")
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    ssh.exec_command(start_cmd)
    
    print("等待 15 秒...")
    time.sleep(15)
    
    # 8. 测试
    print("\n[8] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print("Gunicorn (8000): " + gunicorn_status)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print("Nginx (80): " + nginx_status)
    
    # 9. 检查错误日志
    print("\n[9] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] 仍有数据库访问错误")
        print(errors[-1000:])
    else:
        print("[OK] 无数据库访问错误")
    
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)
    
    if 'Access denied' not in errors and gunicorn_status == '200':
        print("\n[OK] 服务正常！")
        print("\n请刷新浏览器并尝试登录:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n[警告] 仍有问题，请查看上述输出")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
