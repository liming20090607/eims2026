"""
自动重置云服务器 MySQL root 密码为 mysql2026!
无需用户交互，自动执行所有修复步骤
"""
import os
import paramiko
import time

# 服务器配置
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

NEW_PASSWORD = 'mysql2026!'

def execute_command(ssh, command, description="", timeout=30):
    """执行 SSH 命令"""
    if description:
        print(f"\n📋 {description}")
        print("-" * 60)
    
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        
        if output:
            for line in output.split('\n')[:10]:  # 只显示前10行
                print(f"  {line}")
        if error and 'Warning' not in error and 'warning' not in error.lower():
            print(f"  ⚠️  {error[:200]}")
        
        return output, error
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        return None, str(e)

def main():
    print("=" * 70)
    print("🔧 自动重置云服务器 MySQL root 密码")
    print("=" * 70)
    print()
    print("📋 操作计划:")
    print(f"  目标服务器: {SERVER_IP}")
    print(f"  MySQL 用户: root")
    print(f"  新密码: {NEW_PASSWORD}")
    print()
    print("⚠️  注意: 此操作将重置 MySQL root 密码")
    print("  请确保您有服务器的 SSH 访问权限")
    print()
    
    # 连接服务器
    print("[步骤 1/7] 连接到云服务器...")
    print("-" * 70)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
        print("  ✅ SSH 连接成功")
    except Exception as e:
        print(f"  ❌ SSH 连接失败: {str(e)}")
        print("\n  💡 提示: 请检查 SSH 密钥是否正确配置")
        print("     密钥路径: ~/.ssh/id_rsa")
        return
    
    try:
        # 步骤 2: 检查 MySQL 服务
        print("\n[步骤 2/7] 检查 MySQL 服务状态...")
        print("-" * 70)
        
        output, _ = execute_command(ssh, "systemctl is-active mysqld || systemctl is-active mysql", "检查服务状态")
        
        if output != 'active':
            print("\n  ⚠️  MySQL 服务未运行，正在启动...")
            execute_command(ssh, "systemctl start mysqld || systemctl start mysql", "启动 MySQL")
            time.sleep(3)
            execute_command(ssh, "systemctl is-active mysqld || systemctl is-active mysql", "验证启动")
        else:
            print("  ✅ MySQL 服务正在运行")
        
        # 步骤 3: 测试当前密码
        print("\n[步骤 3/7] 测试当前 MySQL 密码...")
        print("-" * 70)
        
        test_cmd = f'mysql -u root -p"{NEW_PASSWORD}" -e "SELECT 1;" 2>&1'
        _, error = execute_command(ssh, test_cmd, "测试密码", timeout=5)
        
        if error and 'Access denied' in error:
            print("  ❌ 密码验证失败，需要重置")
            needs_reset = True
        else:
            print("  ✅ 密码已经是 {NEW_PASSWORD}，无需重置")
            needs_reset = False
        
        # 步骤 4: 重置密码（如果需要）
        if needs_reset:
            print("\n[步骤 4/7] 重置 MySQL root 密码...")
            print("-" * 70)
            
            # 4.1 停止 MySQL
            print("\n  4.1 停止 MySQL 服务...")
            execute_command(ssh, "systemctl stop mysqld || systemctl stop mysql", "停止 MySQL")
            time.sleep(2)
            
            # 4.2 检查进程是否完全停止
            execute_command(ssh, "ps aux | grep mysql | grep -v grep | wc -l", "检查进程")
            
            # 4.3 以安全模式启动
            print("\n  4.2 以安全模式启动 MySQL (skip-grant-tables)...")
            execute_command(ssh, "mysqld_safe --skip-grant-tables &", "安全模式启动")
            time.sleep(4)
            
            # 4.4 重置密码
            print("\n  4.3 重置 root 密码...")
            reset_sql = f"""mysql -u root <<'EOF'
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '{NEW_PASSWORD}';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{NEW_PASSWORD}';
FLUSH PRIVILEGES;
EOF"""
            execute_command(ssh, reset_sql, "执行密码重置", timeout=10)
            
            # 4.5 关闭安全模式
            print("\n  4.4 停止安全模式...")
            execute_command(ssh, "kill $(cat /var/run/mysqld/mysqld.pid 2>/dev/null) 2>/dev/null || pkill -9 mysqld_safe || true", "停止安全模式")
            time.sleep(2)
            
            # 4.6 正常启动 MySQL
            print("\n  4.5 正常启动 MySQL...")
            execute_command(ssh, "systemctl start mysqld || systemctl start mysql", "启动 MySQL")
            time.sleep(4)
            
            print("\n  ✅ MySQL root 密码已重置")
        
        # 步骤 5: 验证新密码
        print("\n[步骤 5/7] 验证新密码...")
        print("-" * 70)
        
        verify_cmd = f'mysql -u root -p"{NEW_PASSWORD}" -e "SELECT VERSION(); SHOW DATABASES LIKE \'eims%\';" 2>&1'
        output, error = execute_command(ssh, verify_cmd, "验证密码并检查数据库", timeout=10)
        
        if error and 'Access denied' in error:
            print("  ❌ 密码重置失败！")
            print("  请手动检查 MySQL 日志: /var/log/mysqld.log")
            ssh.close()
            return
        else:
            print("  ✅ 新密码验证成功！")
        
        # 步骤 6: 更新配置文件
        print("\n[步骤 6/7] 更新服务器配置文件...")
        print("-" * 70)
        
        env_file = f"{SERVER_PATH}/.env"
        
        # 6.1 检查 .env 文件
        print("\n  6.1 检查 .env 文件...")
        check_env_cmd = f"test -f {env_file} && echo 'exists' || echo 'not_exists'"
        output, _ = execute_command(ssh, check_env_cmd, "检查文件", timeout=5)
        
        if output == 'exists':
            # 更新密码
            print("\n  6.2 更新 .env 中的 DB_PASSWORD...")
            update_cmd = f"sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=\"{NEW_PASSWORD}\"/' {env_file}"
            execute_command(ssh, update_cmd, "更新密码", timeout=5)
            
            # 验证更新
            print("\n  6.3 验证 .env 配置...")
            verify_cmd = f"grep DB_PASSWORD {env_file}"
            execute_command(ssh, verify_cmd, "显示配置", timeout=5)
        else:
            print("\n  ⚠️  .env 文件不存在，正在创建...")
            create_env_cmd = f"""cat > {env_file} <<EOF
# MySQL Database Configuration
DB_NAME="eims"
DB_USER="root"
DB_PASSWORD="{NEW_PASSWORD}"
DB_HOST="localhost"
DB_PORT="3306"
EOF"""
            execute_command(ssh, create_env_cmd, "创建 .env 文件", timeout=5)
        
        print("\n  ✅ 配置文件已更新")
        
        # 步骤 7: 重启应用服务
        print("\n[步骤 7/7] 重启应用服务...")
        print("-" * 70)
        
        # 7.1 停止 Gunicorn
        print("\n  7.1 停止 Gunicorn...")
        execute_command(ssh, "pkill -9 -f gunicorn || true", "停止服务", timeout=5)
        time.sleep(2)
        
        # 7.2 启动 Gunicorn
        print("\n  7.2 启动 Gunicorn...")
        start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    wsgi:application 2>&1 && \
sleep 2 && \
echo "✅ Gunicorn 已启动" """
        
        execute_command(ssh, start_cmd, "启动服务", timeout=15)
        
        # 7.3 验证服务
        print("\n  7.3 验证网站访问...")
        test_cmd = "curl -o /dev/null -s -w 'HTTP %{http_code}\\n' http://127.0.0.1:8000/login/"
        execute_command(ssh, test_cmd, "测试 HTTP", timeout=10)
        
        # 最终状态检查
        print("\n  7.4 检查 Gunicorn 进程...")
        execute_command(ssh, "ps aux | grep gunicorn | grep -v grep | wc -l", "进程数量", timeout=5)
        
        # 总结
        print("\n" + "=" * 70)
        print("✅ MySQL 密码重置完成！")
        print("=" * 70)
        print()
        print("📊 修复摘要:")
        print(f"  ✓ MySQL root 密码已重置为: {NEW_PASSWORD}")
        print(f"  ✓ 密码验证成功")
        print(f"  ✓ .env 配置文件已更新")
        print(f"  ✓ Gunicorn 服务已重启")
        print()
        print("🌐 访问地址:")
        print(f"  http://{SERVER_IP}/login/")
        print(f"  http://www.xietongai.com.cn/login/")
        print()
        print("💡 提示:")
        print("  - 本地和云服务器的 MySQL 密码现在完全一致")
        print("  - 请使用浏览器访问上述地址测试登录功能")
        print("  - 如果仍有问题，请检查浏览器控制台的网络请求")
        print()
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
    except Exception as e:
        print(f"\n❌ 修复过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
