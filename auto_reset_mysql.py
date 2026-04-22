#!/usr/bin/env python
"""
自动重置 MySQL root 密码
密码设置为: mysql2026!
"""
import subprocess
import time
import sys
import os

def run_cmd(cmd, shell=False, check=False):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=shell,
            check=check,
            capture_output=True,
            text=True,
            encoding='gbk',
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "命令超时"
    except Exception as e:
        return -1, "", str(e)

print("="*60)
print("🔧 自动重置 MySQL root 密码")
print("目标密码: mysql2026!")
print("="*60)

# 步骤 1: 停止 MySQL 服务
print("\n[1/5] 停止 MySQL80 服务...")
code, out, err = run_cmd('net stop MySQL80', shell=True)
if code == 0 or '成功' in out or 'success' in out.lower():
    print("✅ MySQL 服务已停止")
else:
    print(f"⚠️ 停止服务返回: {out or err}")
    print("尝试强制停止...")
    run_cmd('taskkill /F /IM mysqld.exe', shell=True)
    time.sleep(2)

time.sleep(3)

# 步骤 2: 检查服务状态
print("\n[2/5] 检查服务状态...")
code, out, err = run_cmd('sc query MySQL80', shell=True)
if 'STOPPED' in out or '1  STOPPED' in out:
    print("✅ 确认服务已停止")
else:
    print("⚠️ 服务状态不明确，继续执行...")

# 步骤 3: 启动 MySQL 安全模式（后台）
print("\n[3/5] 启动 MySQL 安全模式（跳过权限验证）...")
mysql_dir = r'C:\Program Files\MySQL\MySQL Server 8.0\bin'
mysqld_exe = os.path.join(mysql_dir, 'mysqld.exe')

if not os.path.exists(mysqld_exe):
    print(f"❌ 找不到 MySQL: {mysqld_exe}")
    print("请检查 MySQL 安装路径")
    sys.exit(1)

# 先清理可能残留的 mysqld 进程
run_cmd('taskkill /F /IM mysqld.exe', shell=True)
time.sleep(2)

# 启动安全模式
print(f"启动: {mysqld_exe} --skip-grant-tables")
proc = subprocess.Popen(
    [mysqld_exe, '--skip-grant-tables'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NO_WINDOW
)

print("⏳ 等待 MySQL 启动（5秒）...")
time.sleep(5)

# 步骤 4: 重置密码
print("\n[4/5] 重置 root 密码...")
mysql_exe = os.path.join(mysql_dir, 'mysql.exe')

# SQL 命令
sql_script = """
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!';
FLUSH PRIVILEGES;
SELECT 1 as success;
exit;
"""

# 写入临时 SQL 文件
sql_file = os.path.join(os.path.dirname(__file__), 'reset_password.sql')
with open(sql_file, 'w', encoding='utf-8') as f:
    f.write(sql_script)

print("执行 SQL 命令...")
try:
    # 使用文件输入方式执行
    with open(sql_file, 'r', encoding='utf-8') as f:
        result = subprocess.run(
            [mysql_exe, '-u', 'root'],
            stdin=f,
            capture_output=True,
            text=True,
            timeout=15,
            encoding='utf-8'
        )
    
    if result.returncode == 0:
        print("✅ 密码重置命令执行成功")
        print(f"输出: {result.stdout}")
    else:
        print(f"⚠️ 返回码: {result.returncode}")
        print(f"输出: {result.stdout}")
        print(f"错误: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("⚠️ SQL 执行超时，但可能已成功")
except Exception as e:
    print(f"⚠️ 执行异常: {e}")
    print("继续执行后续步骤...")

# 清理临时文件
if os.path.exists(sql_file):
    os.remove(sql_file)

# 步骤 5: 重启 MySQL 服务
print("\n[5/5] 重启 MySQL 服务...")

# 先停止安全模式的 MySQL
print("停止安全模式...")
proc.terminate()
try:
    proc.wait(timeout=5)
except:
    proc.kill()

time.sleep(3)

# 强制结束所有 mysqld 进程
print("清理残留进程...")
run_cmd('taskkill /F /IM mysqld.exe', shell=True)
time.sleep(3)

# 启动 MySQL 服务
print("启动 MySQL80 服务...")
code, out, err = run_cmd('net start MySQL80', shell=True)
if code == 0 or '成功' in out or 'success' in out.lower() or 'started' in out.lower():
    print("✅ MySQL 服务已启动")
else:
    print(f"⚠️ 启动结果: {out or err}")
    print("请手动执行: net start MySQL80")

time.sleep(5)

# 验证新密码
print("\n" + "="*60)
print("🔍 验证新密码...")
print("="*60)

try:
    import pymysql
    
    for host in ['localhost', '127.0.0.1']:
        try:
            conn = pymysql.connect(
                host=host,
                port=3306,
                user='root',
                password='mysql2026!',
                charset='utf8mb4',
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()
            cursor.execute('SHOW DATABASES')
            dbs = [db[0] for db in cursor.fetchall()]
            
            print(f"\n✅ 连接成功! (使用 {host})")
            print(f"   MySQL 版本: {version[0]}")
            print(f"   数据库数量: {len(dbs)}")
            print(f"   数据库列表: {dbs}")
            
            # 创建开发数据库
            cursor.execute('CREATE DATABASE IF NOT EXISTS eims2026_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            print(f"\n✅ 已创建/确认开发数据库: eims2026_dev")
            
            conn.close()
            
            print("\n" + "="*60)
            print("🎉 MySQL root 密码重置成功!")
            print("新密码: mysql2026!")
            print("="*60)
            
            sys.exit(0)
            
        except Exception as e:
            print(f"  尝试 {host}: {str(e)[:60]}")
            continue
    
    print("\n❌ 所有主机都连接失败")
    
except ImportError:
    print("❌ 缺少 pymysql 模块")

print("\n如果需要手动重置，请参考:")
print("1. net stop MySQL80")
print("2. mysqld --skip-grant-tables")
print("3. mysql -u root")
print("4. FLUSH PRIVILEGES;")
print("5. ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!';")
print("6. FLUSH PRIVILEGES;")
print("7. exit;")
print("8. net start MySQL80")
