"""
检查超级管理员权限设置
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 要检查的用户列表
usernames = ['admin', '黎绍昆', 'lishaokun', '18978383227']

print("=" * 60)
print("检查超级管理员权限")
print("=" * 60)

for username in usernames:
    try:
        user = User.objects.get(username=username)
        print(f"\n用户名: {user.username}")
        print(f"  is_staff: {user.is_staff}")
        print(f"  is_superuser: {user.is_superuser}")
        print(f"  is_active: {user.is_active}")
        print(f"  可以访问后台管理: {'✓ 是' if (user.is_staff or user.is_superuser) else '✗ 否'}")
    except User.DoesNotExist:
        print(f"\n用户名: {username}")
        print(f"  ✗ 用户不存在")

print("\n" + "=" * 60)
