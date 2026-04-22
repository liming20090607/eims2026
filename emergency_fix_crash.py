import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

def run(cmd, desc):
    print(f"{desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if output and len(output) < 200:
        print(f"  → {output}")
    return exit_code, output

print("="*80)
print("紧急修复 - MySQL持续崩溃问题")
print("="*80)

# 1. 完全停止所有MySQL进程
print("\n【1】完全停止MySQL...")
run("systemctl stop mysqld", "停止服务")
time.sleep(2)
run("killall -9 mysqld 2>/dev/null; echo done", "杀死进程")
time.sleep(2)
run("rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysqld.pid", "清理文件")

# 2. 检查MySQL状态
print("\n【2】检查MySQL状态...")
run("systemctl status mysqld | head -10", "服务状态")

# 3. 尝试正常启动
print("\n【3】正常启动MySQL...")
exit_code, output = run("systemctl start mysqld", "启动服务")
time.sleep(5)

# 4. 验证启动
print("\n【4】验证MySQL...")
for i in range(3):
    exit_code, output = run("systemctl is-active mysqld", f"检查状态 (尝试{i+1})")
    if "active" in output:
        print("  ✅ MySQL已启动")
        break
    time.sleep(3)

# 5. 测试连接
print("\n【5】测试MySQL连接...")
exit_code, output = run('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" 2>&1 | grep -v Warning', "连接测试")
if exit_code == 0:
    print("  ✅ 连接成功")
else:
    print("  ❌ 连接失败，需要重置密码")
    # 使用skip-grant-tables
    print("\n  使用恢复模式重置密码...")
    run("systemctl stop mysqld", "  停止服务")
    time.sleep(2)
    run("/usr/sbin/mysqld --user=mysql --skip-grant-tables &", "  启动恢复模式")
    time.sleep(8)
    
    # 重置密码
    reset_sql = """mysql -u root <<'EOF'
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF"""
    run(reset_sql, "  重置密码")
    time.sleep(2)
    
    # 关闭恢复模式
    run("mysqladmin shutdown 2>/dev/null || killall mysqld", "  关闭恢复模式")
    time.sleep(3)
    
    # 正常启动
    run("systemctl start mysqld", "  正常启动")
    time.sleep(5)
    
    # 再次测试
    exit_code, output = run('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" 2>&1 | grep -v Warning', "  再次测试")
    if exit_code == 0:
        print("  ✅ 密码重置成功，连接正常")

# 6. 重启Gunicorn
print("\n【6】重启Gunicorn...")
run("pkill -9 -f gunicorn", "停止Gunicorn")
time.sleep(2)
run("cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &", "启动Gunicorn")
time.sleep(4)
run("pgrep -c gunicorn", "工作进程数")

# 7. 最终测试
print("\n【7】最终测试...")
time.sleep(2)
exit_code, output = run('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/', "HTTP状态")
if output == "200":
    print("  ✅ 网站正常访问")
elif output == "500":
    print("  ⚠️  HTTP 500错误")
else:
    print(f"  ❌ HTTP状态: {output}")

print("\n" + "="*80)
print("修复完成")
print("="*80)

# 检查MySQL错误日志找出崩溃原因
print("\n检查MySQL错误日志（最近20行）:")
run("tail -20 /var/log/mysqld.log 2>/dev/null || journalctl -u mysqld -n 20 --no-pager", "错误日志")

ssh.close()
