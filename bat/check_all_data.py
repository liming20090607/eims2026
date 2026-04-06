#!/usr/bin/env python3
"""
检查角色数据和权限
"""
import os, sys, django

sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Role, Department
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

print("=" * 60)
print("完整数据检查")
print("=" * 60)

# 1. 检查角色
print("\n1. 角色数据:")
roles = Role.objects.all()
print(f"   数量：{len(roles)}")
for role in roles:
    print(f"   ✓ ID={role.id}, Name={getattr(role, 'name', 'N/A')}")

# 2. 检查部门
print("\n2. 部门数据:")
depts = Department.objects.all()
print(f"   数量：{len(depts)}")
for dept in depts[:5]:  # 只显示前 5 个
    print(f"   ✓ ID={dept.id}, Name={dept.department_name}")

# 3. 检查用户
print("\n3. 用户数据:")
users = User.objects.all()
print(f"   数量：{len(users)}")
for user in users[:5]:  # 只显示前 5 个
    print(f"   ✓ ID={user.id}, Username={user.username}")

# 4. 检查 ContentType
print("\n4. ContentType (eims_app):")
cts = ContentType.objects.filter(app_label='eims_app')
print(f"   数量：{len(cts)}")
for ct in cts:
    print(f"   ✓ {ct.model}")

print("\n完成!")
