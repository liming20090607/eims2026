import paramiko
import time

print("="*70)
print("彻底清理并重启所有服务")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前错误日志
    print("\n[1] 检查当前错误日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    current_errors = stdout.read().decode('utf-8')
    if 'Access denied' in current_errors:
        print("发现数据库访问错误")
        print(current_errors[-1500:])
    else:
        print("无数据库访问错误")
    
    # 2. 杀死所有相关进程
    print("\n[2] 杀死所有 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('killall -9 gunicorn 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
    time.sleep(3)
    
    # 验证进程已杀死
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    procs = stdout.read().decode('utf-8')
    if procs.strip():
        print("警告: 仍有 Gunicorn 进程:")
        print(procs)
        stdin, stdout, stderr = ssh.exec_command('kill -9 $(ps aux | grep gunicorn | grep -v grep | awk \'{print $2}\') 2>/dev/null || true')
        time.sleep(3)
    else:
        print("所有 Gunicorn 进程已杀死")
    
    # 3. 清理 Python 缓存
    print("\n[3] 清理 Python 缓存...")
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true')
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "*.pyc" -delete 2>/dev/null || true')
    print("缓存已清理")
    
    # 4. 清理所有日志
    print("\n[4] 清理所有日志...")
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('> /var/www/eims/logs/access.log')
    stdin, stdout, stderr = ssh.exec_command('echo "" > /var/www/eims/logs/error.log')
    stdin, stdout, stderr = ssh.exec_command('echo "" > /var/www/eims/logs/access.log')
    print("日志已清理")
    
    # 5. 验证配置
    print("\n[5] 验证 settings.py 配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 8 "DATABASES" /var/www/eims/settings.py | head -12')
    db_config = stdout.read().decode('utf-8')
    print("数据库配置:")
    print(db_config)
    
    # 6. 等待端口释放
    print("\n[6] 等待端口 8000 释放...")
    for i in range(5):
        stdin, stdout, stderr = ssh.exec_command('lsof -ti:8000 2>/dev/null')
        port_users = stdout.read().decode('utf-8').strip()
        if not port_users:
            print("端口 8000 已释放")
            break
        else:
            print(f"等待中... ({(i+1)*2}秒)")
            time.sleep(2)
    
    # 7. 启动新的 Gunicorn
    print("\n[7] 启动新的 Gunicorn...")
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
    ssh.exec_command(start_cmd)
    
    print("等待 15 秒让服务启动...")
    time.sleep(15)
    
    # 8. 验证 Gunicorn 进程
    print("\n[8] 验证 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    proc_count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {proc_count}")
    
    # 9. 测试 HTTP
    print("\n[9] 测试 HTTP 访问...")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null')
    gunicorn_status = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn (8000): {gunicorn_status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login/ 2>/dev/null')
    nginx_status = stdout.read().decode('utf-8').strip()
    print(f"Nginx (80): {nginx_status}")
    
    # 10. 等待并检查错误日志
    print("\n[10] 检查错误日志...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if errors.strip():
        print("错误日志内容:")
        print(errors[-2000:])
    else:
        print("错误日志为空（好迹象）")
    
    # 11. 测试 Django 登录
    print("\n[11] 测试 Django 登录...")
    test_login = r'''/var/www/eims/venv/bin/python3 << 'PYEOF'
import os, sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    import django
    django.setup()
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print("DB: OK")
    
    from django.contrib.auth import authenticate
    user = authenticate(username='admin', password='admin123456')
    if user:
        print("Auth admin: OK, ID=" + str(user.id))
    else:
        print("Auth admin: FAIL")
    
    user = authenticate(username='root', password='root123456')
    if user:
        print("Auth root: OK, ID=" + str(user.id))
    else:
        print("Auth root: FAIL")
        
except Exception as e:
    print("FAIL: " + str(e))
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test_login)
    time.sleep(8)
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print("测试结果:")
    print(test_result if test_result else "[无输出]")
    if test_error:
        print("错误:", test_error[:500])
    
    # 12. 再次检查错误日志（看是否有新请求产生的错误）
    print("\n[12] 最终错误日志检查...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/error.log 2>&1')
    final_errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in final_errors:
        print("[X] 仍有数据库访问错误")
        print(final_errors[-2000:])
    else:
        print("[OK] 无数据库访问错误")
    
    print("\n" + "="*70)
    print("完成")
    print("="*70)
    
    if gunicorn_status == '200' and 'DB: OK' in test_result:
        print("\n✅ 服务正常！")
        print("\n请执行以下操作:")
        print("1. 按 Ctrl+Shift+Delete 清除浏览器缓存")
        print("2. 或使用无痕模式 (Ctrl+Shift+N)")
        print("3. 访问 http://39.106.41.239/login/")
        print("   或 http://www.xietongai.com.cn/login/")
        print("\n登录凭据:")
        print("  用户名: admin  密码: admin123456")
        print("  用户名: root   密码: root123456")
    else:
        print("\n⚠️ 仍有问题，请检查上述输出")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
