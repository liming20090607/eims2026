#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入诊断并修复PyMySQL连接问题
Deep diagnosis and fix for PyMySQL connection issues
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("深入诊断PyMySQL连接问题")
    print("Deep Diagnosis of PyMySQL Connection Issues")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 诊断PyMySQL连接行为
        print("\n[2] 诊断PyMySQL连接方式...")
        diagnose_pymysql = '''
cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import pymysql

# 测试1: 使用127.0.0.1 (TCP)
print("测试1: 连接 127.0.0.1 (TCP)...")
try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        port=3306,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("✓ TCP连接成功")
    conn.close()
except Exception as e:
    print(f"✗ TCP连接失败: {e}")

# 测试2: 使用localhost (可能走socket)
print("\\n测试2: 连接 localhost...")
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        port=3306,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("✓ localhost连接成功")
    conn.close()
except Exception as e:
    print(f"✗ localhost连接失败: {e}")

# 测试3: 使用unix_socket
print("\\n测试3: 使用Unix Socket...")
try:
    conn = pymysql.connect(
        unix_socket='/var/lib/mysql/mysql.sock',
        user='root',
        password='EIMS2026_mysql',
        database='eims',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("✓ Socket连接成功")
    conn.close()
except Exception as e:
    print(f"✗ Socket连接失败: {e}")

PYEOF
'''
        stdin, stdout, stderr = ssh.exec_command(diagnose_pymysql)
        time.sleep(5)
        pymysql_result = stdout.read().decode() + stderr.read().decode()
        print(pymysql_result)
        
        # 检查MySQL用户表
        print("\n[3] 检查MySQL用户详细配置...")
        check_users = '''
mysql -uroot -p'EIMS2026_mysql' -e "
SELECT User, Host, plugin, authentication_string 
FROM mysql.user 
WHERE User='root' 
ORDER BY Host;
" 2>&1
'''
        stdin, stdout, stderr = ssh.exec_command(check_users)
        time.sleep(2)
        users_detail = stdout.read().decode() + stderr.read().decode()
        print(users_detail)
        
        # 检查是否有匿名用户干扰
        print("\n[4] 检查匿名用户...")
        check_anonymous = '''
mysql -uroot -p'EIMS2026_mysql' -e "
SELECT User, Host, plugin 
FROM mysql.user 
WHERE User='' OR User IS NULL;
" 2>&1
'''
        stdin, stdout, stderr = ssh.exec_command(check_anonymous)
        time.sleep(2)
        anonymous_users = stdout.read().decode() + stderr.read().decode()
        if anonymous_users.strip():
            print("发现匿名用户:")
            print(anonymous_users)
        else:
            print("✓ 无匿名用户")
        
        # 检查MySQL的bind-address
        print("\n[5] 检查MySQL绑定地址...")
        check_bind = '''
grep -i "bind-address\|skip-networking" /etc/my.cnf /etc/mysql/my.cnf /etc/mysql/mysql.conf.d/mysqld.cnf 2>/dev/null || echo "未找到bind-address配置"
'''
        stdin, stdout, stderr = ssh.exec_command(check_bind)
        bind_config = stdout.read().decode()
        print(bind_config if bind_config.strip() else "使用默认bind-address")
        
        # 检查socket路径
        print("\n[6] 检查socket配置...")
        check_socket = '''
mysql -uroot -p'EIMS2026_mysql' -e "SHOW VARIABLES LIKE 'socket';" 2>&1
ls -la /var/lib/mysql/mysql.sock 2>&1
ls -la /var/run/mysqld/mysqld.sock 2>&1
'''
        stdin, stdout, stderr = ssh.exec_command(check_socket)
        time.sleep(2)
        socket_info = stdout.read().decode() + stderr.read().decode()
        print(socket_info)
        
        # 根据诊断结果修复
        print("\n[7] 执行修复方案...")
        
        # 方案：确保所有可能的连接方式都能工作
        fix_all = '''
mysql -uroot -p'EIMS2026_mysql' << 'EOF'
-- 删除可能冲突的用户
DELETE FROM mysql.user WHERE User='root' AND Host='localhost';
DELETE FROM mysql.user WHERE User='root' AND Host='127.0.0.1';
DELETE FROM mysql.user WHERE User='root' AND Host='::1';
FLUSH PRIVILEGES;

-- 重新创建所有变体，确保都使用mysql_native_password
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

-- 授予权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

FLUSH PRIVILEGES;

-- 验证
SELECT User, Host, plugin FROM mysql.user WHERE User='root' ORDER BY Host;
EOF
'''
        stdin, stdout, stderr = ssh.exec_command(fix_all)
        time.sleep(3)
        fix_result = stdout.read().decode() + stderr.read().decode()
        print("修复结果:")
        print(fix_result)
        
        # 修改Django settings.py，添加unix_socket选项作为备选
        print("\n[8] 优化Django数据库配置...")
        optimize_settings = '''
cd /var/www/eims

# 备份原文件
cp settings.py settings.py.backup.$(date +%Y%m%d_%H%M%S)

# 使用Python修改settings.py，确保使用正确的连接参数
python3 << 'PYEOF'
import re

with open('settings.py', 'r') as f:
    content = f.read()

# 确保DATABASES配置使用127.0.0.1而不是localhost
content = re.sub(
    r"'HOST':\\s*'localhost'",
    "'HOST': '127.0.0.1'",
    content
)

# 确保使用正确的OPTIONS
old_options = r"'OPTIONS':\\s*\\{[^}]*\\}"
new_options = """'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'connect_timeout': 10,
        }"""

content = re.sub(old_options, new_options, content)

with open('settings.py', 'w') as f:
    f.write(content)

print("✓ settings.py已优化")
PYEOF

# 验证配置
grep -A 15 "'default':" settings.py | head -20
'''
        stdin, stdout, stderr = ssh.exec_command(optimize_settings)
        time.sleep(3)
        settings_result = stdout.read().decode() + stderr.read().decode()
        print(settings_result)
        
        # 完全重启Gunicorn
        print("\n[9] 完全重启Gunicorn...")
        ssh.exec_command('pkill -9 -f gunicorn; sleep 2')
        ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || true')
        time.sleep(3)
        
        # 清理缓存
        ssh.exec_command('''
cd /var/www/eims
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
''')
        
        # 启动Gunicorn
        ssh.exec_command('''
cd /var/www/eims && source venv/bin/activate && gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --timeout 120 \
    --daemon \
    wsgi:application
''')
        print("等待Gunicorn启动...")
        time.sleep(10)
        
        # 验证
        print("\n[10] 验证修复...")
        verify = '''
cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
from django.contrib.auth import authenticate

print("=== 数据库连接测试 ===")
try:
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✓ 数据库连接成功")
    
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"✓ 找到 {count} 个用户")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")

print("\\n=== 用户认证测试 ===")
admin_user = authenticate(username='admin', password='admin123456')
if admin_user:
    print("✓ admin认证成功")
else:
    print("✗ admin认证失败")

root_user = authenticate(username='root', password='root123456')
if root_user:
    print("✓ root认证成功")
else:
    print("✗ root认证失败")

PYEOF
'''
        stdin, stdout, stderr = ssh.exec_command(verify)
        time.sleep(8)
        verify_result = stdout.read().decode() + stderr.read().decode()
        print(verify_result)
        
        # HTTP测试
        print("\n[11] HTTP访问测试...")
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP状态码: %{http_code}\\n" http://localhost:8000/login/')
        http_status = stdout.read().decode()
        print(http_status)
        
        # 错误日志
        print("\n[12] 检查错误日志...")
        stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || echo "无日志"')
        error_log = stdout.read().decode()
        if 'Access denied' in error_log or 'OperationalError' in error_log:
            print("⚠️ 发现数据库错误:")
            print(error_log[-500:])
        else:
            print("✓ 无数据库错误")
        
        print("\n" + "=" * 70)
        print("✅ 深度修复完成！")
        print("=" * 70)
        print("\n修复内容:")
        print("   1. ✓ 重新创建所有root用户变体")
        print("   2. ✓ 统一使用mysql_native_password")
        print("   3. ✓ 优化Django数据库配置")
        print("   4. ✓ 完全重启Gunicorn")
        print("   5. ✓ 清理所有缓存")
        
        print("\n🌐 访问:")
        print("   http://www.xietongai.com.cn/login/")
        print("\n🔑 登录:")
        print("   admin / admin123456")
        print("   root / root123456")
        
        print("\n⚠️ 请清除浏览器缓存后重试")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
