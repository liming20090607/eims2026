import paramiko
import time

print("="*70)
print("MySQL 认证问题修复")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前 settings.py 配置
    print("\n[1] 检查 Django settings.py 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 10 "DATABASES" /var/www/eims/settings.py | head -20')
    db_config = stdout.read().decode('utf-8')
    print("数据库配置:")
    print(db_config)
    
    # 2. 检查 MySQL 用户认证
    print("\n[2] 检查 MySQL root 用户认证方式...")
    stdin, stdout, stderr = ssh.exec_command('''mysql -uroot -pEIMS2026_mysql -h 127.0.0.1 -e "SELECT User, Host, plugin FROM mysql.user WHERE User='root';" 2>&1''')
    user_info = stdout.read().decode('utf-8')
    user_error = stderr.read().decode('utf-8')
    print("MySQL root 用户信息:")
    if user_info.strip():
        print(user_info)
    else:
        print("错误:", user_error.strip()[:200])
    
    # 3. 确保 settings.py 使用 127.0.0.1
    print("\n[3] 确保 settings.py 使用 127.0.0.1...")
    
    fix_settings = '''python3 << 'PYEOF'
with open('/var/www/eims/settings.py', 'r') as f:
    content = f.read()

# 确保使用 127.0.0.1
if "'HOST': 'localhost'," in content:
    content = content.replace("'HOST': 'localhost',", "'HOST': '127.0.0.1',")
    with open('/var/www/eims/settings.py', 'w') as f:
        f.write(content)
    print("已修改 HOST 为 127.0.0.1")
else:
    print("HOST 配置正确")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(fix_settings)
    settings_result = stdout.read().decode('utf-8')
    print(settings_result)
    
    # 4. 重启 Gunicorn
    print("\n[4] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn || true')
    time.sleep(3)
    
    # 清空日志
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    
    # 启动 Gunicorn
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    ssh.exec_command(start_cmd)
    
    print("等待 10 秒让服务启动...")
    time.sleep(10)
    
    # 5. 测试 HTTP
    print("\n[5] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print("Gunicorn (8000): " + gunicorn_status)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print("Nginx (80): " + nginx_status)
    
    # 6. 检查错误日志
    print("\n[6] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] 仍有数据库访问错误")
        print(errors[-1000:])
    else:
        print("[OK] 无数据库访问错误")
    
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)
    
    if gunicorn_status == '200' and nginx_status == '200':
        print("\n[OK] 服务正常运行！")
        print("\n现在可以尝试登录:")
        print("  http://39.106.41.239/login/")
        print("  http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n[警告] 服务状态异常，请检查上述输出")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
