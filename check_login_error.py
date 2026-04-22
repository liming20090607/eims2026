import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("检查登录错误原因")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查 Gunicorn 错误日志
    print("\n[1] 检查 Gunicorn 错误日志（最近 50 行）...")
    stdin, stdout, stderr = ssh.exec_command('tail -100 /var/www/eims/logs/error.log 2>&1')
    error_log = stdout.read().decode('utf-8')
    print(error_log[-3000:] if len(error_log) > 3000 else error_log)
    
    # 2. 检查 Gunicorn 访问日志
    print("\n[2] 检查 Gunicorn 访问日志（最近 20 行）...")
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/access.log 2>&1')
    access_log = stdout.read().decode('utf-8')
    print(access_log)
    
    # 3. 检查 login view 代码
    print("\n[3] 检查自定义登录视图代码...")
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "*custom_login*" -o -name "*login*" -path "*/views*" 2>/dev/null | grep -E "\.py$" | grep -v __pycache__ | head -10')
    login_files = stdout.read().decode('utf-8')
    print("登录相关文件:")
    print(login_files)
    
    # 4. 查看 login view 的数据库操作
    print("\n[4] 检查 login view 中的数据库连接...")
    stdin, stdout, stderr = ssh.exec_command('grep -r "def custom_login\|def login" /var/www/eims/eims_app/views/ --include="*.py" -l 2>/dev/null | head -5')
    login_view_files = stdout.read().decode('utf-8')
    print("包含登录函数的文件:")
    print(login_view_files)
    
    # 5. 检查是否有多个数据库配置
    print("\n[5] 检查 settings.py 中是否有多个数据库...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 50 "DATABASES" /var/www/eims/settings.py | grep -E "DATABASES|\'ENGINE\'|\'NAME\'|\'USER\'|\'PASSWORD\'|\'HOST\'|\'PORT\'" | head -30')
    db_configs = stdout.read().decode('utf-8')
    print(db_configs)
    
    # 6. 模拟登录请求测试
    print("\n[6] 模拟登录请求测试...")
    
    test_login_script = r'''
import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import authenticate
from django.db import connection

print("测试数据库连接:")
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print("✓ 数据库连接成功")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")

print("\n测试用户认证:")
# 测试 admin 用户
try:
    user = authenticate(username='admin', password='admin123456')
    if user:
        print(f"✓ admin 认证成功 (ID: {user.id})")
    else:
        print("✗ admin 认证失败: 用户名或密码错误")
except Exception as e:
    print(f"✗ admin 认证异常: {e}")
    import traceback
    traceback.print_exc()

# 测试 root 用户
try:
    user = authenticate(username='root', password='root123456')
    if user:
        print(f"✓ root 认证成功 (ID: {user.id})")
    else:
        print("✗ root 认证失败: 用户名或密码错误")
except Exception as e:
    print(f"✗ root 认证异常: {e}")
    import traceback
    traceback.print_exc()

print("\n检查数据库中存在的用户:")
from django.contrib.auth.models import User
users = User.objects.filter(is_active=True)[:10]
for u in users:
    print(f"  - {u.username} (ID: {u.id}, 超级管理员: {u.is_superuser})")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_auth.py << "AUTHEOF"\n{test_login_script}\nAUTHEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_auth.py 2>&1')
    auth_output = stdout.read().decode('utf-8')
    auth_error = stderr.read().decode('utf-8')
    print(auth_output)
    if auth_error:
        print("\n错误:", auth_error[:500])
    
    # 7. 检查是否有 Django 缓存或连接池问题
    print("\n[7] 检查 Django 配置中的连接设置...")
    stdin, stdout, stderr = ssh.exec_command('grep -E "CONN_MAX_AGE|POOL" /var/www/eims/settings.py 2>/dev/null || echo "无连接池配置"')
    conn_config = stdout.read().decode('utf-8')
    print(conn_config)
    
    # 8. 重启 Gunicorn 并测试
    print("\n[8] 完全重启 Gunicorn 服务...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f "gunicorn.*eims" || true')
    time.sleep(3)
    
    # 确认进程已停止
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    process_count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数（重启前）: {process_count}")
    
    # 重新启动
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    time.sleep(5)
    
    # 验证进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    process_count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数（重启后）: {process_count}")
    
    # 9. HTTP 测试
    print("\n[9] HTTP 测试...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status_code}")
    
    # 10. 测试登录页面
    print("\n[10] 测试登录页面...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ | head -50')
    login_page = stdout.read().decode('utf-8')
    if 'login' in login_page.lower() or 'form' in login_page.lower():
        print("✓ 登录页面正常")
    else:
        print("登录页面内容（前 500 字符）:")
        print(login_page[:500])
    
    print("\n" + "="*70)
    if status_code in ['200', '302']:
        print("✅ 系统运行正常")
        print("="*70)
        print("\n如果仍然遇到登录错误，请尝试:")
        print("1. 清除浏览器缓存和 Cookie")
        print("2. 使用无痕模式访问")
        print("3. 检查浏览器控制台是否有 JavaScript 错误")
    else:
        print(f"⚠️ 状态码异常: {status_code}")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
