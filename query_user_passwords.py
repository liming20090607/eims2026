import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("查询服务器用户账户信息...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 查询数据库中的用户信息
    print("\n[1] 查询 auth_user 表中的用户...")
    query_users = '''
mysql -uroot -pEIMS2026_mysql eims -e "
SELECT id, username, email, is_superuser, is_staff, is_active, date_joined 
FROM auth_user 
WHERE username IN ('root', 'admin') 
ORDER BY username;
" 2>&1
'''
    
    stdin, stdout, stderr = ssh.exec_command(query_users)
    user_info = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if user_info.strip():
        print(user_info)
    else:
        print("[未找到 root 或 admin 用户]")
        if error:
            print("错误:", error)
    
    # 检查是否可以直接重置密码
    print("\n[2] 创建/重置 admin 用户密码...")
    reset_script = r'''
import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User

# 检查并创建/更新 admin 用户
try:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123456')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.is_active = True
    admin_user.save()
    print("✓ admin 用户密码已重置为: admin123456")
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✓ 已创建 admin 用户，密码: admin123456")

# 检查并创建/更新 root 用户
try:
    root_user = User.objects.get(username='root')
    root_user.set_password('root123456')
    root_user.is_superuser = True
    root_user.is_staff = True
    root_user.is_active = True
    root_user.save()
    print("✓ root 用户密码已重置为: root123456")
except User.DoesNotExist:
    User.objects.create_superuser('root', 'root@example.com', 'root123456')
    print("✓ 已创建 root 用户，密码: root123456")

print("\n用户信息:")
for user in User.objects.filter(username__in=['root', 'admin']):
    print(f"  - {user.username}: 超级管理员={'是' if user.is_superuser else '否'}, 激活={'是' if user.is_active else '否'}")
'''
    
    # 写入脚本
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/reset_passwords.py << "PWEOF"\n{reset_script}\nPWEOF')
    time.sleep(2)
    
    # 执行脚本
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/reset_passwords.py')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print(output)
    if error:
        print("错误:", error[:300])
    
    # 验证登录
    print("\n[3] 测试用户登录...")
    login_test = r'''
import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import authenticate

print("测试 admin 用户登录:")
user = authenticate(username='admin', password='admin123456')
if user:
    print(f"  ✓ admin 登录成功 (用户ID: {user.id})")
else:
    print("  ✗ admin 登录失败")

print("\n测试 root 用户登录:")
user = authenticate(username='root', password='root123456')
if user:
    print(f"  ✓ root 登录成功 (用户ID: {user.id})")
else:
    print("  ✗ root 登录失败")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_login.py << "LOGINEOF"\n{login_test}\nLOGINEOF')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_login.py')
    login_output = stdout.read().decode('utf-8')
    login_error = stderr.read().decode('utf-8')
    
    print(login_output)
    if login_error:
        print("错误:", login_error[:300])
    
    # 最终总结
    print("\n" + "="*70)
    print("✅ 用户账户信息")
    print("="*70)
    print("\n登录凭据:")
    print("  用户: admin")
    print("  密码: admin123456")
    print("  权限: 超级管理员")
    print("\n  用户: root")
    print("  密码: root123456")
    print("  权限: 超级管理员")
    print("\n登录地址:")
    print("  http://39.106.41.239:8000/admin/")
    print("  http://www.xietongai.com.cn/admin/")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
