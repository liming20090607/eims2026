import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("深度诊断数据库连接问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查所有 settings.py 文件
    print("\n[1] 查找所有 settings.py 文件...")
    stdin, stdout, stderr = ssh.exec_command('find / -name "settings.py" -path "*/eims*" -o -name "settings.py" -path "*/EIMS*" 2>/dev/null | head -20')
    settings_files = stdout.read().decode('utf-8')
    print(settings_files)
    
    # 2. 检查 /var/www/eims/settings.py 实际内容
    print("\n[2] 检查 /var/www/eims/settings.py 数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 20 "DATABASES" /var/www/eims/settings.py | head -25')
    settings_db = stdout.read().decode('utf-8')
    print(settings_db)
    
    # 3. 检查是否有 .env 文件覆盖配置
    print("\n[3] 检查 .env 文件...")
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name ".env" -o -name ".env.*" 2>/dev/null')
    env_files = stdout.read().decode('utf-8')
    if env_files.strip():
        print("找到 .env 文件:")
        print(env_files)
        for env_file in env_files.strip().split('\n'):
            if env_file:
                print(f"\n{env_file} 内容:")
                stdin, stdout, stderr = ssh.exec_command(f'cat {env_file}')
                print(stdout.read().decode('utf-8'))
    else:
        print("未找到 .env 文件")
    
    # 4. 检查环境变量
    print("\n[4] 检查环境变量中的数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('env | grep -i "DB_\|DATABASE\|MYSQL" 2>/dev/null || echo "无相关环境变量"')
    env_vars = stdout.read().decode('utf-8')
    print(env_vars)
    
    # 5. 检查 Gunicorn 启动脚本和环境
    print("\n[5] 检查 Gunicorn 进程详情...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    gunicorn_info = stdout.read().decode('utf-8')
    print(gunicorn_info)
    
    # 6. 检查 systemd service 文件（如果有）
    print("\n[6] 检查 systemd 服务配置...")
    stdin, stdout, stderr = ssh.exec_command('find /etc/systemd -name "*eims*" -o -name "*gunicorn*" 2>/dev/null | head -5')
    service_files = stdout.read().decode('utf-8')
    if service_files.strip():
        print("服务文件:")
        print(service_files)
        for svc in service_files.strip().split('\n'):
            if svc:
                print(f"\n{svc} 内容:")
                stdin, stdout, stderr = ssh.exec_command(f'cat {svc}')
                print(stdout.read().decode('utf-8'))
    
    # 7. 实时测试 Django 数据库连接
    print("\n[7] 实时测试 Django 数据库连接...")
    
    test_script = r'''
import os
import sys

# 确保使用正确的项目路径
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

print(f"Python path: {sys.path[:5]}")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    import django
    django.setup()
    print("Django setup successful")
    
    from django.conf import settings
    print(f"\nDATABASES 配置:")
    print(f"  ENGINE: {settings.DATABASES['default']['ENGINE']}")
    print(f"  NAME: {settings.DATABASES['default']['NAME']}")
    print(f"  USER: {settings.DATABASES['default']['USER']}")
    print(f"  HOST: {settings.DATABASES['default']['HOST']}")
    print(f"  PORT: {settings.DATABASES['default']['PORT']}")
    
    # 隐藏密码
    password = settings.DATABASES['default']['PASSWORD']
    masked_password = password[:3] + '*' * (len(password) - 3) if len(password) > 3 else '***'
    print(f"  PASSWORD: {masked_password} (length: {len(password)})")
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f"\n✓ 数据库连接成功: {result}")
    
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f"✓ 数据库中有 {len(tables)} 个表")
    
except Exception as e:
    print(f"\n✗ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/full_db_test.py << "TESTEOF"\n{test_script}\nTESTEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/full_db_test.py 2>&1')
    test_output = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print(test_output)
    if test_error:
        print("\n错误:", test_error[:500])
    
    # 8. 检查 MySQL 实际认证插件
    print("\n[8] 检查 MySQL root 用户认证插件...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT user, host, plugin, authentication_string FROM mysql.user WHERE user=\'root\';" 2>&1')
    auth_info = stdout.read().decode('utf-8')
    print(auth_info)
    
    # 9. 尝试用 PyMySQL 直接连接（模拟 Django）
    print("\n[9] 用 PyMySQL 直接连接测试...")
    
    pymysql_test = r'''
import pymysql

print("尝试连接 MySQL...")
print("  host: localhost")
print("  user: root")
print("  database: eims")
print("  port: 3306")

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        port=3306,
        charset='utf8mb4'
    )
    print("✓ PyMySQL 连接成功")
    cursor = conn.cursor()
    cursor.execute('SELECT USER(), CURRENT_USER()')
    user_info = cursor.fetchone()
    print(f"  用户: {user_info[0]}")
    print(f"  当前用户: {user_info[1]}")
    conn.close()
except Exception as e:
    print(f"✗ PyMySQL 连接失败: {e}")
    import traceback
    traceback.print_exc()
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/pymysql_test.py << "PTESTEOF"\n{pymysql_test}\nPTESTEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/pymysql_test.py 2>&1')
    pymysql_output = stdout.read().decode('utf-8')
    pymysql_error = stderr.read().decode('utf-8')
    print(pymysql_output)
    if pymysql_error:
        print("\n错误:", pymysql_error[:500])
    
    print("\n" + "="*70)
    print("诊断完成")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
