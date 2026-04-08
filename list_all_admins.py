"""
列出所有管理员用户
"""
import os
import sys
import django

sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("所有管理员用户列表")
print("=" * 60)

# 查询所有是管理员的用户
admin_users = User.objects.filter(is_superuser=True)

print(f"\n共找到 {admin_users.count()} 个超级管理员:\n")

for i, user in enumerate(admin_users, 1):
    print(f"{i}. 用户名: {user.username}")
    print(f"   全名: {user.get_full_name() or '未设置'}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   is_active: {user.is_active}")
    print()

# 也列出所有 is_staff=True 的用户
staff_users = User.objects.filter(is_staff=True).exclude(is_superuser=True)
print(f"\n共有 {staff_users.count()} 个普通管理员（is_staff=True 但不是超级管理员）:\n")

for i, user in enumerate(staff_users, 1):
    print(f"{i}. 用户名: {user.username}")
    print(f"   全名: {user.get_full_name() or '未设置'}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print()

print("=" * 60)
