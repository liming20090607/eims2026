"""
检查 admin 用户权限设置
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

# 查找 admin 用户
try:
    admin_user = User.objects.get(username='admin')
    print(f"用户名: {admin_user.username}")
    print(f"is_staff: {admin_user.is_staff}")
    print(f"is_superuser: {admin_user.is_superuser}")
    print(f"is_active: {admin_user.is_active}")
    print(f"\n判断结果:")
    print(f"是否可以访问后台管理: {admin_user.is_staff or admin_user.is_superuser}")
except User.DoesNotExist:
    print("未找到 admin 用户")
