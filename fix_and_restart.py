#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 MySQL 密码配置并重启服务
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
    print("🔧 修复 MySQL 密码配置")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n正在连接服务器...")
        ssh.connect(
            hostname='124.71.169.138',
            username='root',
            password='EIMS2026_ssh',
            timeout=15
        )
        print("✅ 已连接服务器\n")
        
        # 步骤 1：检查当前 settings.py 配置
        print("[1] 检查当前 settings.py 数据库配置...")
        check_cmd = '''grep -n "PASSWORD" /var/www/eims/eims/settings.py | grep -v "^#"'''
        _, result, error = ssh_exec(ssh, check_cmd)
        print(f"   当前配置:\n{result}")
        
        # 步骤 2：修复密码配置
        print("\n[2] 修复所有数据库配置中的密码...")
        fix_cmd = '''cd /var/www/eims/eims && sed -i "s/'PASSWORD': '[^']*'/'PASSWORD': 'EIMS2026_mysql'/g" settings.py'''
        _, result, error = ssh_exec(ssh, fix_cmd)
        print("   ✅ 密码配置已更新")
        
        # 步骤 3：验证修复结果
        print("\n[3] 验证修复后的配置...")
        verify_cmd = '''grep -n "PASSWORD" /var/www/eims/eims/settings.py | grep -v "^#"'''
        _, result, error = ssh_exec(ssh, verify_cmd)
        print(f"   修复后配置:\n{result}")
        
        # 步骤 4：重启 Gunicorn
        print("\n[4] 重启 Gunicorn 服务...")
        restart_cmd = '''pkill -9 gunicorn; sleep 2; cd /var/www/eims && nohup venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 120 --chdir /var/www/eims eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 & sleep 3 && echo "✅ Gunicorn 已重启" && pgrep -c gunicorn | xargs echo "Worker 数量:"'''
        _, result, error = ssh_exec(ssh, restart_cmd)
        print(f"   {result}")
        
        # 步骤 5：测试登录页面
        print("\n[5] 测试登录页面...")
        test_cmd = '''curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:80/login/'''
        _, result, error = ssh_exec(ssh, test_cmd)
        print(f"   登录页面状态: {result}")
        
        # 步骤 6：检查错误日志
        print("\n[6] 检查最新的错误日志...")
        log_cmd = '''tail -20 /var/www/eims/logs/gunicorn_error.log | grep -i "error\|exception" | tail -5'''
        _, result, error = ssh_exec(ssh, log_cmd)
        if result.strip():
            print(f"   错误日志:\n{result}")
        else:
            print("   ✅ 没有发现新的错误")
        
        print("\n" + "=" * 70)
        print("✅ 修复完成！")
        print("=" * 70)
        print("\n现在请访问: http://www.xietongai.com.cn/login/")
        print("\n如果仍有问题，请告诉我具体的错误信息。")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
