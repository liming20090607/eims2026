#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 MySQL 连接和登录功能
"""
import paramiko
import time

def ssh_exec(ssh, command):
    """通过 SSH 执行命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    return stdin, result, error

def main():
    print("=" * 70)
    print("🔍 验证 MySQL 连接和登录功能")
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
        
        # 步骤 1：清空错误日志
        print("[1] 清空旧的错误日志...")
        clear_cmd = '''echo "" > /var/www/eims/logs/gunicorn_error.log'''
        ssh_exec(ssh, clear_cmd)
        print("   ✅ 错误日志已清空")
        
        # 步骤 2：测试登录页面（触发数据库连接）
        print("\n[2] 测试登录页面（会触发数据库连接）...")
        test_cmd = '''curl -s http://127.0.0.1:80/login/ | grep -o "<title>.*</title>"'''
        _, result, error = ssh_exec(ssh, test_cmd)
        if '登录' in result:
            print(f"   ✅ 登录页面正常: {result.strip()}")
        else:
            print(f"   ⚠️  页面内容: {result[:100]}")
        
        # 步骤 3：等待 2 秒让可能的错误记录到日志
        print("\n[3] 等待 2 秒...")
        time.sleep(2)
        
        # 步骤 4：检查新的错误日志
        print("\n[4] 检查新的错误日志...")
        log_cmd = '''tail -30 /var/www/eims/logs/gunicorn_error.log'''
        _, result, error = ssh_exec(ssh, log_cmd)
        
        if 'OperationalError' in result or 'Access denied' in result:
            print("   ❌ 仍然有 MySQL 连接错误:")
            print(result)
            
            # 显示具体的错误配置
            print("\n[5] 检查 settings.py 中的数据库配置...")
            db_cmd = '''grep -A 8 "'default':" /var/www/eims/eims/settings.py | head -10'''
            _, result, error = ssh_exec(ssh, db_cmd)
            print(f"   配置内容:\n{result}")
            
            print("\n[6] 测试 MySQL 连接...")
            mysql_test = '''mysql -u root -p"EIMS2026_mysql" -e "SHOW DATABASES;" 2>&1 | head -15'''
            _, result, error = ssh_exec(ssh, mysql_test)
            print(f"   MySQL 测试结果:\n{result}")
            
        else:
            print("   ✅ 没有新的错误！MySQL 连接正常。")
            print("\n" + "=" * 70)
            print("✅ 系统运行正常！")
            print("=" * 70)
            print("\n现在可以正常登录系统了:")
            print("   http://www.xietongai.com.cn/login/")
            print("\n⚠️  注意: 由于还没有创建 admin/root 账户，")
            print("   您需要先创建账户才能登录。")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
