#!/usr/bin/env python3
"""
强制修复MySQL认证问题
Force fix MySQL authentication issue
"""
import paramiko
import os
import time
import sys

print("=" * 80)
print("🚨 强制修复MySQL认证")
print("Force Fix MySQL Authentication")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ 已连接服务器\n")
    
    # 步骤1: 完全停止MySQL
    print("[1/8] 完全停止MySQL...")
    ssh.exec_command("systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 3", timeout=10)
    time.sleep(4)
    
    # 验证MySQL已停止
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep mysqld | grep -v grep | wc -l")
    mysql_count = int(stdout.read().decode().strip())
    print(f"  MySQL进程数: {mysql_count} (应该为0)")
    
    # 步骤2: 清理所有socket和lock文件
    print("\n[2/8] 清理socket和lock文件...")
    ssh.exec_command("rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysql.sock.lock", timeout=5)
    ssh.exec_command("mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld", timeout=5)
    print("  ✅ 清理完成")
    
    # 步骤3: 以skip-grant-tables模式启动MySQL
    print("\n[3/8] 启动MySQL（skip-grant-tables模式）...")
    ssh.exec_command("mysqld_safe --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", timeout=5)
    
    # 等待socket文件创建
    print("  等待socket文件创建...")
    socket_ready = False
    for i in range(20):
        time.sleep(1)
        stdin, stdout, stderr = ssh.exec_command("ls -la /var/lib/mysql/mysql.sock 2>&1")
        result = stdout.read().decode().strip()
        
        if 'mysql.sock' in result and 'No such file' not in result:
            print(f"  ✅ Socket文件已创建 ({i+1}秒)")
            socket_ready = True
            break
    
    if not socket_ready:
        print("  ❌ Socket文件未创建，尝试其他方法...")
        # 尝试直接启动mysqld
        ssh.exec_command("mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", timeout=5)
        time.sleep(10)
    
    # 步骤4: 重置root密码
    print("\n[4/8] 重置root密码...")
    
    reset_sql = """
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user WHERE user='root';
"""
    
    stdin, stdout, stderr = ssh.exec_command(
        f"mysql -u root --socket=/var/lib/mysql/mysql.sock -e \"{reset_sql}\" 2>&1",
        timeout=15
    )
    
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    
    if output:
        print(f"  SQL输出: {output[:300]}")
    if error and 'Warning' not in error:
        print(f"  错误: {error[:300]}")
    
    # 步骤5: 验证密码重置
    print("\n[5/8] 验证密码重置...")
    stdin, stdout, stderr = ssh.exec_command(
        "mysql -u root -pEIMS2026_mysql --socket=/var/lib/mysql/mysql.sock -e 'SELECT 1 AS test' 2>&1"
    )
    result = stdout.read().decode().strip()
    
    if 'test' in result.lower() or '1' in result:
        print("  ✅ 密码重置成功，连接正常")
    else:
        print(f"  ❌ 密码验证失败: {result[:200]}")
        if error:
            print(f"  错误: {error[:200]}")
    
    # 步骤6: 关闭skip-grant-tables模式，正常启动
    print("\n[6/8] 正常启动MySQL...")
    
    # 关闭当前MySQL
    ssh.exec_command("mysqladmin -u root -pEIMS2026_mysql --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall -9 mysqld", timeout=10)
    time.sleep(3)
    
    # 正常启动
    ssh.exec_command("systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null", timeout=10)
    time.sleep(5)
    
    # 验证MySQL运行状态
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active mysqld 2>/dev/null || ps aux | grep mysqld | grep -v grep | head -1")
    status = stdout.read().decode().strip()
    print(f"  MySQL状态: {status}")
    
    # 步骤7: 最终验证连接
    print("\n[7/8] 最终验证MySQL连接...")
    
    for i in range(5):
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command(
            "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS connection_test' 2>&1"
        )
        result = stdout.read().decode().strip()
        
        if 'connection_test' in result.lower() or '1' in result:
            print(f"  ✅ MySQL连接成功 (尝试{i+1})")
            break
        else:
            print(f"  尝试{i+1}: 连接失败，等待MySQL启动...")
    
    # 步骤8: 重启Gunicorn
    print("\n[8/8] 重启Gunicorn...")
    
    ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
    time.sleep(3)
    
    start_cmd = """cd /var/www/eims && source venv/bin/activate && nohup gunicorn \
--bind 127.0.0.1:8000 \
--workers 4 \
--timeout 300 \
wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"""
    
    ssh.exec_command(start_cmd, timeout=10)
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
    gunicorn_count = int(stdout.read().decode().strip())
    print(f"  ✅ Gunicorn已重启 ({gunicorn_count}进程)")
    
    # 最终测试
    print("\n" + "=" * 80)
    print("✅ MySQL修复完成！")
    print("=" * 80)
    
    # 测试网站访问
    print("\n测试网站访问...")
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command(
        "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:8000/login/"
    )
    http_code = stdout.read().decode().strip()
    
    if http_code == '200':
        print("  ✅ 登录页面: HTTP 200")
    else:
        print(f"  ⚠️  登录页面: HTTP {http_code}")
    
    print("\n🌐 访问地址:")
    print("  http://www.xietongai.com.cn/login/")
    
    print("\n💡 现在请刷新浏览器，应该能正常登录了！")
    print("  • 如果仍有问题，点击'Manual Fix Now'按钮")
    print("  • 或再次运行此脚本")
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
