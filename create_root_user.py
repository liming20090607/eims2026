"""
Create 'root' superuser account
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*80)
print("创建 root 超级管理员账号...")
print("="*80)

# Check if root user already exists
if User.objects.filter(username='root').exists():
    print("\n✓ 用户 'root' 已存在")
    root_user = User.objects.get(username='root')
    root_user.set_password('root123456')
    root_user.is_superuser = True
    root_user.is_staff = True
    root_user.is_active = True
    root_user.save()
    print("✓ 已更新 root 用户权限和密码")
else:
    # Create root superuser
    root_user = User.objects.create_superuser(
        username='root',
        email='root@eims.com',
        password='root123456'
    )
    print("\n✓ 超级管理员 'root' 创建成功！")

print("\n" + "="*80)
print("登录信息:")
print("="*80)
print(f"  用户名: root")
print(f"  密码: root123456")
print(f"  权限: 超级管理员（可访问所有系统）")
print("\n⚠️  请立即修改密码！")
print("="*80)
