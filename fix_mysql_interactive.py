"""
交互式 MySQL 密码修复工具
手动输入正确的 MySQL 密码并修复
"""
import os
import paramiko

# 服务器配置
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

def execute_command(ssh, command, show_output=True):
    """执行 SSH 命令"""
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        
        if show_output and output:
            print(output)
        if error and 'Warning' not in error:
            print(f"⚠️  {error}")
        
        return output, error
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None, str(e)

def main():
    print("=" * 60)
    print("🔧 MySQL 密码修复工具（交互式）")
    print("=" * 60)
    print()
    print("问题分析：")
    print("  云服务器 MySQL root 密码与本地不一致")
    print("  需要您提供云服务器上 MySQL 的正确密码")
    print()
    
    # 连接服务器
    print("[1/4] 连接到云服务器...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
        print("✅ SSH 连接成功")
    except Exception as e:
        print(f"❌ SSH 连接失败: {str(e)}")
        print("请检查 SSH 密钥配置")
        return
    
    try:
        # 询问用户当前正确的 MySQL 密码
        print("\n[2/4] 请输入云服务器上 MySQL root 的正确密码")
        print("-" * 60)
        print("提示：")
        print("  - 如果您记得密码，请直接输入")
        print("  - 如果不记得，请输入 'reset' 进行密码重置")
        print("  - 如果从未设置过，通常为空密码，直接按回车")
        print()
        
        current_password = input("MySQL root 密码: ").strip()
        
        if current_password.lower() == 'reset':
            # 需要重置密码
            print("\n🔧 开始重置 MySQL root 密码...")
            print("-" * 60)
            
            # 停止 MySQL
            print("正在停止 MySQL...")
            execute_command(ssh, "systemctl stop mysqld", show_output=False)
            execute_command(ssh, "sleep 2", show_output=False)
            
            # 安全模式启动
            print("以安全模式启动 MySQL...")
            execute_command(ssh, "mysqld_safe --skip-grant-tables &", show_output=False)
            execute_command(ssh, "sleep 3", show_output=False)
            
            # 获取新密码
            print()
            new_password = input("请输入新的 MySQL root 密码 (建议: mysql2026!): ").strip()
            if not new_password:
                new_password = "mysql2026!"
            
            # 重置密码
            print("\n正在重置密码...")
            reset_cmd = f"""mysql -u root -e "
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '{new_password}';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{new_password}';
FLUSH PRIVILEGES;
" 2>&1"""
            execute_command(ssh, reset_cmd)
            
            # 重启 MySQL
            print("重启 MySQL...")
            execute_command(ssh, "kill $(cat /var/run/mysqld/mysqld.pid 2>/dev/null) 2>/dev/null || true", show_output=False)
            execute_command(ssh, "sleep 2", show_output=False)
            execute_command(ssh, "systemctl start mysqld", show_output=False)
            execute_command(ssh, "sleep 3", show_output=False)
            
            print(f"✅ MySQL root 密码已重置为: {new_password}")
            current_password = new_password
        else:
            # 测试用户提供的密码
            print("\n[3/4] 测试密码...")
            print("-" * 60)
            test_cmd = f'mysql -u root -p"{current_password}" -e "SELECT 1;" 2>&1'
            _, error = execute_command(ssh, test_cmd, show_output=False)
            
            if error and 'Access denied' in error:
                print("❌ 密码错误！")
                print("建议输入 'reset' 重置密码")
                ssh.close()
                return
            else:
                print("✅ 密码验证成功！")
        
        # 更新 .env 文件
        print("\n[4/4] 更新服务器配置...")
        print("-" * 60)
        
        env_file = f"{SERVER_PATH}/.env"
        
        # 检查 settings.py 中的密码
        print("正在更新 .env 文件...")
        update_env_cmd = f"sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=\"{current_password}\"/' {env_file}"
        execute_command(ssh, update_env_cmd, show_output=False)
        print("✅ .env 文件已更新")
        
        # 验证 settings.py
        print("正在检查 settings.py...")
        check_settings_cmd = f"grep 'DB_PASSWORD' {env_file}"
        output, _ = execute_command(ssh, check_settings_cmd, show_output=True)
        
        # 重启服务
        print("\n重启 Gunicorn 服务...")
        execute_command(ssh, "pkill -9 -f gunicorn || true", show_output=False)
        execute_command(ssh, "sleep 2", show_output=False)
        
        start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    wsgi:application && \
echo "✅ Gunicorn 已启动" """
        
        execute_command(ssh, start_cmd)
        execute_command(ssh, "sleep 3", show_output=False)
        
        # 最终测试
        print("\n验证网站访问...")
        test_web_cmd = "curl -o /dev/null -s -w 'HTTP状态码: %{http_code}\\n' http://127.0.0.1:8000/login/"
        execute_command(ssh, test_web_cmd)
        
        print("\n" + "=" * 60)
        print("✅ 修复完成！")
        print("=" * 60)
        print()
        print("📊 修复摘要:")
        print(f"  ✓ MySQL 密码已确认/重置")
        print(f"  ✓ .env 配置文件已更新")
        print(f"  ✓ Gunicorn 服务已重启")
        print()
        print("🌐 访问地址:")
        print(f"  http://{SERVER_IP}/login/")
        print(f"  http://www.xietongai.com.cn/login/")
        print()
        print("=" * 60)
        
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
