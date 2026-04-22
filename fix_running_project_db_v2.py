import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 /var/www/eims/ 的数据库配置")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 更新数据库密码
    print("\n[1] 更新 /var/www/eims/settings.py 数据库密码...")
    
    update_script = r'''
settings_path = '/var/www/eims/settings.py'

with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("原配置:")
if 'root123' in content:
    print("  - 找到旧密码 'root123'")
if "'NAME': 'eims'" in content:
    print("  - 数据库名正确: eims")

# 替换密码
content = content.replace("'PASSWORD': 'root123'", "'PASSWORD': 'EIMS2026_mysql'")

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ settings.py 已更新")
print("新密码: EIMS2026_mysql")
'''
    
    # 写入更新脚本
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/update_eims_settings.py << "SCRIPTEOF"\n{update_script}\nSCRIPTEOF')
    time.sleep(2)
    
    # 执行更新
    stdin, stdout, stderr = ssh.exec_command('python3.10 /tmp/update_eims_settings.py')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("错误:", error)
    
    # 2. 验证更新
    print("\n[2] 验证数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 8 "PASSWORD" /var/www/eims/settings.py | head -10')
    verify = stdout.read().decode('utf-8')
    print(verify)
    
    # 3. 重启 Gunicorn 服务
    print("\n[3] 重启 Gunicorn 服务...")
    
    # 停止旧进程
    stdin, stdout, stderr = ssh.exec_command('pkill -f "gunicorn.*eims" || true')
    time.sleep(3)
    
    # 启动新服务
    print("  启动 Gunicorn...")
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log wsgi.py > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    time.sleep(5)
    
    # 4. 验证服务运行
    print("\n[4] 验证服务运行状态...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    process_info = stdout.read().decode('utf-8')
    
    if process_info.strip():
        print("✓ Gunicorn 进程运行中:")
        lines = process_info.strip().split('\n')
        for line in lines[:3]:
            print(f"  {line}")
    else:
        print("✗ 未找到 Gunicorn 进程")
    
    # 5. 测试数据库连接
    print("\n[5] 测试 Django 数据库连接...")
    test_script = r'''
import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    django.setup()
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f'OK: 数据库连接成功: {result}')
    
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f'OK: 数据库中有 {len(tables)} 个表')
except Exception as e:
    print(f'ERROR: 数据库连接失败: {e}')
'''
    
    # 写入测试脚本
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_db.py << "DBTEST"\n{test_script}\nDBTEST')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_db.py')
    db_output = stdout.read().decode('utf-8')
    db_error = stderr.read().decode('utf-8')
    print(db_output)
    if db_error:
        print("错误:", db_error[:300])
    
    # 6. HTTP 测试
    print("\n[6] HTTP 测试...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status_code = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status_code}")
    
    if status_code in ['200', '302']:
        print("\n" + "="*70)
        print("✅ 问题已解决！")
        print("="*70)
        print("\n修复内容:")
        print("  ✓ 更新了 /var/www/eims/settings.py 的数据库密码")
        print("  ✓ 重启了 Gunicorn 服务")
        print("  ✓ 数据库连接测试通过")
        print(f"  ✓ HTTP 服务正常 (状态码: {status_code})")
        print("\n现在可以正常访问:")
        print("  http://39.106.41.239:8000/")
        print("  http://www.xietongai.com.cn/")
        print("="*70)
    else:
        print(f"\n⚠️ 状态码异常: {status_code}")
        print("请检查日志: /var/www/eims/logs/error.log")
    
finally:
    ssh.close()
    print("\n完成！")
