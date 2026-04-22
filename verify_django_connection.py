import paramiko
import time

print("="*70)
print("最终验证 - Django 数据库连接")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 测试 Django 数据库连接
    print("\n[1] 测试 Django 数据库连接...")
    
    test_script = r'''python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    import django
    django.setup()
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print('SUCCESS: Django database connection OK')
    
    from django.contrib.auth import authenticate
    
    user = authenticate(username='admin', password='admin123456')
    if user:
        print('SUCCESS: admin auth OK, ID=' + str(user.id))
    else:
        print('FAIL: admin auth failed')
    
    user = authenticate(username='root', password='root123456')
    if user:
        print('SUCCESS: root auth OK, ID=' + str(user.id))
    else:
        print('FAIL: root auth failed')
        
except Exception as e:
    print('FAIL: ' + str(e))
    import traceback
    traceback.print_exc()
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_script)
    time.sleep(10)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print("测试结果:")
    print(result if result else "[无输出]")
    if error:
        print("错误:", error[:500])
    
    # 2. 测试 HTTP
    print("\n[2] 测试 HTTP 访问...")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print("Gunicorn (8000): " + gunicorn_status)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print("Nginx (80): " + nginx_status)
    
    # 3. 检查错误日志
    print("\n[3] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[X] 仍有数据库访问错误")
    else:
        print("[OK] 无数据库访问错误")
    
    if errors.strip():
        print("日志:")
        print(errors[-500:])
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)
    
    if 'SUCCESS: Django database connection OK' in result:
        print("\n[OK] Django 数据库连接正常！")
        if 'SUCCESS: admin auth OK' in result:
            print("[OK] 用户认证成功！")
            print("\n访问地址:")
            print("  http://39.106.41.239/login/")
            print("  http://www.xietongai.com.cn/login/")
            print("\n登录凭据:")
            print("  用户名: admin  密码: admin123456")
            print("  用户名: root   密码: root123456")
        else:
            print("\n[警告] 数据库连接正常但用户认证可能有问题")
    else:
        print("\n[失败] Django 数据库连接失败")
        print("请查看上述错误信息")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
