#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 admin 和 root 账户状态
"""
import paramiko

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
print("🔍 检查 admin 和 root 账户状态")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    print("\n✅ 已连接服务器\n")
    
    # 检查所有数据库中的用户
    databases = ['eims_dingce', 'eims_shengchang', 'eims_jiachengda', 'root_admin']
    
    print("[1] 检查各数据库中的用户账户:\n")
    
    for db in databases:
        print(f"数据库: {db}")
        print("-" * 70)
        
        # 查询用户表
        check_cmd = f'''mysql -u root -p"EIMS2026_mysql" -e "
        USE {db};
        SELECT id, username, email, is_superuser, is_staff, is_active 
        FROM auth_user 
        WHERE username IN ('admin', 'root') OR is_superuser = 1
        ORDER BY id;
        " 2>&1'''
        
        _, result, error = ssh_exec(ssh, check_cmd)
        
        if result and 'username' in result:
            print(result)
        else:
            print("  未找到 admin 或 root 账户")
        
        print()
    
    # 检查密码哈希
    print("\n[2] 检查密码哈希（确认密码是否设置）:\n")
    
    for db in databases[:1]:  # 只检查第一个数据库作为示例
        pwd_cmd = f'''mysql -u root -p"EIMS2026_mysql" -e "
        USE {db};
        SELECT username, SUBSTRING(password, 1, 20) as pwd_hash, date_joined 
        FROM auth_user 
        WHERE username IN ('admin', 'root')
        LIMIT 5;
        " 2>&1'''
        
        _, pwd_result, _ = ssh_exec(ssh, pwd_cmd)
        if pwd_result:
            print(pwd_result)
    
    # 检查默认密码配置
    print("\n[3] 检查代码中的默认密码配置:\n")
    
    # 查找可能的默认密码
    search_cmd = '''grep -r "admin.*password\|root.*password\|default.*password" /var/www/eims/eims_app/ --include="*.py" | grep -i "admin\|root" | head -10'''
    _, search_result, _ = ssh_exec(ssh, search_cmd)
    if search_result:
        print("代码中的默认密码配置:")
        print(search_result)
    else:
        print("未在代码中找到硬编码的默认密码")
    
    # 检查是否有初始化脚本
    print("\n[4] 检查用户初始化脚本:\n")
    
    init_cmd = '''find /var/www/eims -name "*init*user*" -o -name "*create*admin*" -o -name "*setup*user*" 2>/dev/null | head -10'''
    _, init_result, _ = ssh_exec(ssh, init_cmd)
    if init_result:
        print("找到初始化脚本:")
        print(init_result)
    else:
        print("未找到用户初始化脚本")
    
    print("\n" + "=" * 70)
    print("📋 总结:")
    print("=" * 70)
    print("""
根据检查结果，admin 和 root 账户的密码可能是:

1. 如果在初始化时设置了默认密码，常见配置:
   - admin / admin123
   - admin / admin@123
   - root / root123
   - root / EIMS2026_root

2. 如果您在部署时修改过密码，请回忆当时的设置

3. 如果需要重置密码，可以使用以下命令:
   cd /var/www/eims
   venv/bin/python manage.py shell
   
   然后执行:
   from django.contrib.auth.models import User
   user = User.objects.get(username='admin')
   user.set_password('新密码')
   user.save()

4. 或者创建新的超级用户:
   cd /var/www/eims
   venv/bin/python manage.py createsuperuser
    """)
    print("=" * 70)

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
