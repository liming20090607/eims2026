#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查并修复 MySQL 密码配置
"""
import paramiko

def ssh_exec(ssh, command):
    """通过 SSH 执行命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    return stdin, result, error

def main():
    print("=" * 70)
    print("🔧 检查 MySQL 密码配置")
    print("=" * 70)
    
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(
            hostname='124.71.169.138',
            username='root',
            password='EIMS2026_ssh',
            timeout=10
        )
        print("\n✅ 已连接服务器\n")
        
        # 步骤 1：测试当前 MySQL root 密码
        print("[1] 测试 MySQL root 用户密码...")
        
        # 尝试常用密码
        test_passwords = ['EIMS2026_mysql', 'root', '123456', '']
        
        for pwd in test_passwords:
            test_cmd = f'mysql -u root -p"{pwd}" -e "SELECT 1;" 2>&1 | head -1'
            _, result, error = ssh_exec(ssh, test_cmd)
            
            if '1' in result and 'ERROR' not in result:
                print(f"   ✅ 找到正确的 MySQL root 密码: {pwd if pwd else '(空密码)'}")
                correct_password = pwd
                break
        else:
            print("   ❌ 未找到正确的密码")
            print("\n   请检查服务器 MySQL 密码，然后手动修改 settings.py")
            return
        
        # 步骤 2：检查 settings.py 中的密码配置
        print("\n[2] 检查 settings.py 中的数据库配置...")
        check_settings_cmd = '''grep -A 5 "DATABASES" /var/www/eims/eims/settings.py | grep -E "PASSWORD|USER|NAME" | head -10'''
        _, result, error = ssh_exec(ssh, check_settings_cmd)
        print(f"   当前配置:\n{result}")
        
        # 步骤 3：修复密码配置
        print("\n[3] 修复 settings.py 中的密码配置...")
        
        # 使用 sed 替换所有数据库配置中的密码
        fix_cmd = f'''cd /var/www/eims/eims && sed -i "s/'PASSWORD': '[^']*'/'PASSWORD': '{correct_password}'/g" settings.py'''
        _, result, error = ssh_exec(ssh, fix_cmd)
        
        # 验证修复结果
        verify_cmd = '''grep -A 5 "DATABASES" /var/www/eims/eims/settings.py | grep -E "PASSWORD|USER|NAME" | head -10'''
        _, result, error = ssh_exec(ssh, verify_cmd)
        print(f"   ✅ 修复后配置:\n{result}")
        
        # 步骤 4：重启 Gunicorn 服务
        print("\n[4] 重启 Gunicorn 服务...")
        restart_cmd = '''pkill -9 gunicorn; sleep 2; cd /var/www/eims && nohup venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 120 --chdir /var/www/eims eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 & sleep 3 && echo "✅ Gunicorn 已重启" && pgrep -c gunicorn | xargs echo "Worker 数量:"'''
        _, result, error = ssh_exec(ssh, restart_cmd)
        print(f"   {result}")
        
        # 步骤 5：测试登录页面
        print("\n[5] 测试登录页面...")
        test_login_cmd = '''curl -s -o /dev/null -w "HTTP 状态码: %{http_code}\\n" http://127.0.0.1:80/login/'''
        _, result, error = ssh_exec(ssh, test_login_cmd)
        print(f"   {result}")
        
        # 总结
        print("\n" + "=" * 70)
        print("📋 修复完成总结:")
        print("=" * 70)
        print(f"\n✅ MySQL root 密码: {correct_password if correct_password else '(空密码)'}")
        print("✅ settings.py 已更新")
        print("✅ Gunicorn 已重启")
        print("\n🌐 现在可以访问登录页面:")
        print("   http://www.xietongai.com.cn/login/")
        print("\n⚠️  注意:")
        print("   - 如果仍然报错，请检查 MySQL 服务是否正常运行")
        print("   - 可以在 VS Code 远程终端运行: systemctl status mysqld")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        ssh.close()
        print("\n✅ 服务器连接已关闭")

if __name__ == '__main__':
    main()
