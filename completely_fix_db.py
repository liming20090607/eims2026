import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("彻底修复数据库连接问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 删除旧的 root@localhost 并重新创建
    print("\n[1] 完全删除并重建 root@localhost 用户...")
    
    recreate_user_script = '''mysql -uroot -pEIMS2026_mysql << 'MYSQL_EOF'
-- 删除旧的 root 用户（如果存在）
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'127.0.0.1';
DROP USER IF EXISTS 'root'@'::1';

-- 创建新的 root 用户
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- 授予所有权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证
SELECT user, host, plugin FROM mysql.user WHERE user='root';
MYSQL_EOF
'''
    
    stdin, stdout, stderr = ssh.exec_command(recreate_user_script)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error and 'Warning' not in error:
        print("错误:", error[:500])
    
    # 2. 查看 login view 代码
    print("\n[2] 检查自定义登录视图代码...")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/eims/eims_app/views/views_custom_login.py')
    login_code = stdout.read().decode('utf-8')
    print("自定义登录视图代码（前 100 行）:")
    print(login_code[:3000])
    
    # 3. 清空 Gunicorn 错误日志
    print("\n[3] 清空错误日志...")
    stdin, stdout, stderr = ssh.exec_command('echo "" > /var/www/eims/logs/error.log')
    print("✓ 错误日志已清空")
    
    # 4. 完全停止并重启 Gunicorn
    print("\n[4] 完全重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f "gunicorn.*eims" || true')
    time.sleep(3)
    
    # 确认进程已完全停止
    stdin, stdout, stderr = ssh.exec_command('sleep 2; ps aux | grep gunicorn | grep -v grep | wc -l')
    count = stdout.read().decode('utf-8').strip()
    print(f"停止后进程数: {count}")
    
    # 启动新进程
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    time.sleep(8)
    
    # 验证进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    new_count = stdout.read().decode('utf-8').strip()
    print(f"启动后进程数: {new_count}")
    
    # 5. 等待并检查新的错误日志
    print("\n[5] 检查新的错误日志...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/error.log 2>&1')
    new_errors = stdout.read().decode('utf-8')
    if new_errors.strip() and 'Access denied' not in new_errors:
        print("错误日志内容:")
        print(new_errors[-1000:] if len(new_errors) > 1000 else new_errors)
    elif 'Access denied' in new_errors:
        print("[✗] 仍有 Access denied 错误")
        print(new_errors[-1500:])
    else:
        print("[✓] 无新错误")
    
    # 6. HTTP 测试
    print("\n[6] HTTP 测试...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status}")
    
    # 7. 检查 settings.py 的 DATABASES 配置是否使用环境变量
    print("\n[7] 检查 settings.py 数据库配置逻辑...")
    stdin, stdout, stderr = ssh.exec_command('head -100 /var/www/eims/settings.py')
    settings_head = stdout.read().decode('utf-8')
    
    # 查看是否有 os.environ.get 用于数据库配置
    if 'os.environ.get' in settings_head or 'os.getenv' in settings_head:
        print("[!] 发现环境变量配置")
        stdin, stdout, stderr = ssh.exec_command('grep -n "DB_PASSWORD\|DATABASES" /var/www/eims/settings.py | head -20')
        print(stdout.read().decode('utf-8'))
    else:
        print("[✓] 未使用环境变量配置数据库")
    
    # 8. 测试完整的登录流程
    print("\n[8] 测试登录 POST 请求...")
    
    test_post_login = r'''
import os
import sys
import django
import json

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import authenticate

# 测试数据库连接
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print("✓ 数据库连接成功")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 POST 登录
client = Client()
response = client.post('/login/', {
    'username': 'admin',
    'password': 'admin123456'
}, follow=True)

print(f"\n登录响应状态码: {response.status_code}")
print(f"重定向次数: {len(response.redirect_chain)}")
if response.redirect_chain:
    print(f"重定向到: {response.redirect_chain[-1][0]}")

if response.status_code == 200:
    print("✓ 登录成功！")
else:
    print(f"✗ 登录失败，状态码: {response.status_code}")
    print(f"响应内容（前 500 字符）: {response.content.decode('utf-8', errors='ignore')[:500]}")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_post_login.py << "POSTEOF"\n{test_post_login}\nPOSTEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_post_login.py 2>&1')
    post_output = stdout.read().decode('utf-8')
    post_error = stderr.read().decode('utf-8')
    print(post_output)
    if post_error:
        print("\n错误:", post_error[:500])
    
    print("\n" + "="*70)
    print("修复完成，请尝试登录:")
    print("  http://www.xietongai.com.cn/login/")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
