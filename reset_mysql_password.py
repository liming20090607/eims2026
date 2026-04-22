#!/usr/bin/env python
import subprocess
import time
import os
import signal

print("="*60)
print("重置 MySQL root 密码为: mysql2026!")
print("="*60)

# 步骤1：停止 MySQL 服务
print("\n[步骤1] 停止 MySQL80 服务...")
try:
    subprocess.run(['net', 'stop', 'MySQL80'], check=True, capture_output=True, text=True)
    print("✅ MySQL 服务已停止")
    time.sleep(2)
except subprocess.CalledProcessError as e:
    print(f"❌ 停止服务失败: {e}")
    print("请手动以管理员身份运行命令: net stop MySQL80")
    exit(1)

# 步骤2：安全模式启动 MySQL（跳过密码验证）
print("\n[步骤2] 以安全模式启动 MySQL...")
mysql_dir = r'C:\Program Files\MySQL\MySQL Server 8.0\bin'
mysql_safe_path = os.path.join(mysql_dir, 'mysqld.exe')

if not os.path.exists(mysql_safe_path):
    print(f"❌ 找不到 MySQL: {mysql_safe_path}")
    print("请检查 MySQL 安装路径")
    exit(1)

# 启动安全模式
print(f"启动: {mysql_safe_path} --skip-grant-tables")
proc = subprocess.Popen(
    [mysql_safe_path, '--skip-grant-tables'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

print("⏳ 等待 MySQL 启动...")
time.sleep(5)

# 步骤3：重置密码
print("\n[步骤3] 重置 root 密码...")
mysql_path = os.path.join(mysql_dir, 'mysql.exe')

sql_commands = """
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!';
FLUSH PRIVILEGES;
exit;
"""

try:
    result = subprocess.run(
        [mysql_path, '-u', 'root'],
        input=sql_commands,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("✅ 密码重置成功!")
    else:
        print(f"❌ 密码重置失败:")
        print(f"错误: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("⚠️ 命令超时，但密码可能已重置")
except Exception as e:
    print(f"❌ 执行失败: {e}")

# 步骤4：停止安全模式的 MySQL
print("\n[步骤4] 停止安全模式的 MySQL...")
proc.terminate()
time.sleep(3)

# 强制结束可能的残留进程
subprocess.run(['taskkill', '/F', '/IM', 'mysqld.exe'], 
               stdout=subprocess.PIPE, 
               stderr=subprocess.PIPE)
time.sleep(2)

# 步骤5：正常启动 MySQL 服务
print("\n[步骤5] 正常启动 MySQL80 服务...")
try:
    subprocess.run(['net', 'start', 'MySQL80'], check=True, capture_output=True, text=True)
    print("✅ MySQL 服务已启动")
except subprocess.CalledProcessError as e:
    print(f"⚠️ 启动服务失败: {e}")
    print("请手动启动: net start MySQL80")

# 步骤6：验证新密码
print("\n[步骤6] 验证新密码...")
time.sleep(3)

try:
    import pymysql
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql2026!',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    cursor.execute('SHOW DATABASES')
    dbs = [db[0] for db in cursor.fetchall()]
    print(f"✅ 验证成功!")
    print(f"   MySQL {version[0]}")
    print(f"   数据库: {dbs}")
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 MySQL root 密码已重置为: mysql2026!")
    print("="*60)
    
except Exception as e:
    print(f"❌ 验证失败: {e}")
    print("\n可能需要手动完成:")
    print("1. 以管理员身份运行 cmd")
    print("2. net stop MySQL80")
    print(f'3. "{mysql_safe_path}" --skip-grant-tables')
    print("4. 在另一个终端: mysql -u root")
    print("5. 执行: FLUSH PRIVILEGES; ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!'; FLUSH PRIVILEGES;")
    print("6. 重启 MySQL 服务: net start MySQL80")

print("\n✅ 重置流程完成")
