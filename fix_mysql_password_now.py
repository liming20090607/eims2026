#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
紧急修复MySQL密码问题
"""
import paramiko
import time

SSH_HOST = '39.106.41.239'
SSH_USER = 'root'
SSH_PASS = 'EIMS2026_root'

def ssh_exec(ssh, command, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_status, output, error

print("=" * 70)
print("🚨 紧急修复MySQL密码问题")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ 已连接到服务器\n")
    
    # 步骤1：诊断当前settings.py中的密码
    print("[1] 检查 settings.py 中的MySQL密码配置...")
    _, pwd_lines, _ = ssh_exec(ssh, 'grep -n "PASSWORD" /var/www/eims/eims/settings.py | head -10')
    print(f"当前配置：\n{pwd_lines}\n")
    
    # 步骤2：测试MySQL密码
    print("[2] 测试MySQL连接...")
    
    # 测试正确的密码
    _, test_result, _ = ssh_exec(ssh, 'mysql -u root -p"EIMS2026_mysql" -e "SELECT 1;" 2>&1')
    if '1' in test_result:
        print("  ✅ MySQL密码 'EIMS2026_mysql' 正确\n")
        correct_password = 'EIMS2026_mysql'
    else:
        print("  ❌ 密码 'EIMS2026_mysql' 失败，尝试重置...\n")
        correct_password = None
    
    # 步骤3：修复settings.py
    if 'EIMS2026_mysql' not in pwd_lines:
        print("[3] 修复 settings.py 中的密码配置...")
        
        # 使用sed替换所有错误的密码
        fix_cmd = "sed -i \"s/'PASSWORD': '[^']*'/'PASSWORD': 'EIMS2026_mysql'/g\" /var/www/eims/eims/settings.py"
        ssh_exec(ssh, fix_cmd)
        
        # 验证修复
        _, fixed_lines, _ = ssh_exec(ssh, 'grep -n "PASSWORD" /var/www/eims/eims/settings.py | head -10')
        print(f"修复后：\n{fixed_lines}\n")
    else:
        print("[3] settings.py 密码配置已正确 ✅\n")
    
    # 步骤4：重启Gunicorn
    print("[4] 重启Gunicorn服务...")
    ssh_exec(ssh, 'pkill -9 gunicorn || true')
    time.sleep(2)
    
    start_cmd = '''cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn \
        --bind 127.0.0.1:8000 \
        --workers 5 \
        --timeout 120 \
        --chdir /var/www/eims \
        eims.wsgi:application \
        --access-logfile /var/www/eims/logs/gunicorn_access.log \
        --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'''
    
    ssh_exec(ssh, start_cmd)
    time.sleep(5)
    
    _, count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    print(f"  ✅ Gunicorn 工作进程数: {count}\n")
    
    # 步骤5：测试登录页面
    print("[5] 测试登录页面...")
    _, code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
    print(f"  HTTP状态码: {code}\n")
    
    # 如果还是失败，查看详细错误
    if code not in ['200', '302']:
        print("[6] 查看最近的错误日志...")
        _, errors, _ = ssh_exec(ssh, 'tail -20 /var/www/eims/logs/gunicorn_error.log')
        print(f"错误日志：\n{errors}\n")
    
    print("=" * 70)
    if code in ['200', '302']:
        print("✅ 修复成功！系统现在应该可以正常登录了")
        print("\n🌐 访问地址:")
        print("   http://www.xietongai.com.cn/login/")
        print("   http://39.106.41.239/login/")
    else:
        print("⚠️ 仍有问题，请检查上面的错误日志")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
