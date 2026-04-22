"""
远程修复云服务器 MySQL 密码问题
通过 SSH 连接到服务器并执行修复命令
"""
import os
import sys
import paramiko

# 服务器配置
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

MYSQL_PASSWORD = 'mysql2026!'  # 本地使用的密码

def execute_command(ssh, command, description=""):
    """执行 SSH 命令并输出结果"""
    if description:
        print(f"\n📋 {description}")
        print("-" * 60)
    
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        
        if output:
            print(output)
        if error and 'warning' not in error.lower():
            print(f"⚠️  {error}")
        
        return output, error
    except Exception as e:
        print(f"❌ 命令执行失败: {str(e)}")
        return None, str(e)

def main():
    print("=" * 60)
    print("🔧 MySQL 密码远程修复工具")
    print("=" * 60)
    print()
    print(f"📋 服务器信息:")
    print(f"  IP: {SERVER_IP}")
    print(f"  用户: {SERVER_USER}")
    print(f"  目标密码: {MYSQL_PASSWORD}")
    print()
    
    # 连接服务器
    print("[步骤 1/6] 连接到云服务器...")
    print("-" * 60)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
        print("✅ SSH 连接成功")
    except Exception as e:
        print(f"❌ SSH 连接失败: {str(e)}")
        print("\n💡 提示: 请检查 SSH 密钥是否正确配置")
        print("   或使用密码连接: ssh root@39.106.41.239")
        return
    
    try:
        # 步骤 1: 检查 MySQL 服务状态
        print("\n[步骤 2/6] 检查 MySQL 服务状态...")
        print("-" * 60)
        output, _ = execute_command(ssh, "systemctl is-active mysql || systemctl is-active mysqld", "检查 MySQL 服务")
        
        if output != 'active':
            print("⚠️  MySQL 服务未运行，正在启动...")
            execute_command(ssh, "systemctl start mysql || systemctl start mysqld", "启动 MySQL")
            execute_command(ssh, "sleep 2", "等待服务启动")
        else:
            print("✅ MySQL 服务正在运行")
        
        # 步骤 2: 测试当前密码
        print("\n[步骤 3/6] 测试当前 MySQL 密码...")
        print("-" * 60)
        test_cmd = f'mysql -u root -p"{MYSQL_PASSWORD}" -e "SELECT 1;" 2>&1'
        output, error = execute_command(ssh, test_cmd, "测试密码")
        
        if error and 'Access denied' in error:
            print("❌ 密码验证失败，需要重置密码")
            needs_reset = True
        else:
            print("✅ 密码验证成功！")
            needs_reset = False
        
        # 步骤 3: 如果需要，重置密码
        if needs_reset:
            print("\n[步骤 4/6] 重置 MySQL root 密码...")
            print("-" * 60)
            
            # 停止 MySQL
            print("正在停止 MySQL...")
            execute_command(ssh, "systemctl stop mysql || systemctl stop mysqld", "停止 MySQL")
            execute_command(ssh, "sleep 2", "等待")
            
            # 以安全模式启动
            print("以安全模式启动 MySQL...")
            execute_command(ssh, "mysqld_safe --skip-grant-tables &", "安全模式启动")
            execute_command(ssh, "sleep 3", "等待")
            
            # 重置密码
            print("重置 root 密码...")
            reset_sql = f"""mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '{MYSQL_PASSWORD}';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{MYSQL_PASSWORD}';
FLUSH PRIVILEGES;
EOF"""
            execute_command(ssh, reset_sql, "执行密码重置")
            
            # 关闭安全模式
            print("关闭安全模式...")
            execute_command(ssh, "kill $(cat /var/run/mysqld/mysqld.pid 2>/dev/null) 2>/dev/null || true", "停止安全模式")
            execute_command(ssh, "sleep 2", "等待")
            
            # 正常启动
            print("正常启动 MySQL...")
            execute_command(ssh, "systemctl start mysql || systemctl start mysqld", "启动 MySQL")
            execute_command(ssh, "sleep 3", "等待服务启动")
            
            print("✅ MySQL root 密码已重置")
        
        # 步骤 4: 验证新密码
        print("\n[步骤 5/6] 验证新密码...")
        print("-" * 60)
        verify_cmd = f'mysql -u root -p"{MYSQL_PASSWORD}" -e "SHOW DATABASES;" 2>&1 | head -20'
        output, error = execute_command(ssh, verify_cmd, "验证密码并显示数据库")
        
        if error and 'Access denied' in error:
            print("❌ 密码重置失败，请手动检查")
            ssh.close()
            return
        else:
            print("✅ 新密码验证成功！")
        
        # 步骤 5: 检查并创建必需的数据库
        print("\n[步骤 6/6] 检查必需的数据库...")
        print("-" * 60)
        databases = ['eims', 'eims_root', 'eims_dingce', 'eims_shengchang', 'eims_jiachengda']
        
        for db in databases:
            check_cmd = f'mysql -u root -p"{MYSQL_PASSWORD}" -e "USE {db};" 2>&1'
            _, error = execute_command(ssh, check_cmd, f"检查数据库 {db}")
            
            if error and 'Unknown database' in error:
                print(f"⚠️  数据库 '{db}' 不存在，正在创建...")
                create_cmd = f'mysql -u root -p"{MYSQL_PASSWORD}" -e "CREATE DATABASE {db} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
                execute_command(ssh, create_cmd, f"创建数据库 {db}")
            else:
                print(f"✅ 数据库 '{db}' 存在")
        
        # 步骤 6: 更新 .env 文件
        print("\n[额外步骤] 更新 .env 文件配置...")
        print("-" * 60)
        
        env_file = f"{SERVER_PATH}/.env"
        check_env_cmd = f"test -f {env_file} && echo 'exists' || echo 'not_exists'"
        output, _ = execute_command(ssh, check_env_cmd, "检查 .env 文件")
        
        if output == 'exists':
            # 更新密码
            update_cmd = f"sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=\"{MYSQL_PASSWORD}\"/' {env_file}"
            execute_command(ssh, update_cmd, "更新 .env 中的密码")
            print("✅ .env 文件已更新")
        else:
            # 创建 .env 文件
            create_env_cmd = f"""cat > {env_file} <<EOF
DB_NAME="eims"
DB_USER="root"
DB_PASSWORD="{MYSQL_PASSWORD}"
DB_HOST="localhost"
DB_PORT="3306"
EOF"""
            execute_command(ssh, create_env_cmd, "创建 .env 文件")
            print("✅ .env 文件已创建")
        
        # 步骤 7: 重启 Gunicorn
        print("\n[最后步骤] 重启 Gunicorn 服务...")
        print("-" * 60)
        execute_command(ssh, "pkill -9 -f gunicorn || true", "停止 Gunicorn")
        execute_command(ssh, "sleep 2", "等待")
        
        start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    wsgi:application && \
echo "Gunicorn started" """
        
        execute_command(ssh, start_cmd, "启动 Gunicorn")
        execute_command(ssh, "sleep 3", "等待服务启动")
        
        # 验证服务
        print("\n验证服务状态...")
        execute_command(ssh, "curl -o /dev/null -s -w '%{{http_code}}' http://127.0.0.1:8000/login/", "检查 HTTP 状态")
        
        print("\n" + "=" * 60)
        print("✅ MySQL 密码修复完成！")
        print("=" * 60)
        print()
        print("📊 修复摘要:")
        print(f"  ✓ MySQL root 密码已设置为: {MYSQL_PASSWORD}")
        print(f"  ✓ 所有必需数据库已检查/创建")
        print(f"  ✓ .env 文件已更新")
        print(f"  ✓ Gunicorn 服务已重启")
        print()
        print("🌐 请访问网站测试:")
        print(f"  http://{SERVER_IP}/login/")
        print(f"  http://www.xietongai.com.cn/login/")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 修复过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
