#!/usr/bin/env python3
"""
检查并清理 XTCOAI 公司关联数据
"""
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')

import django
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models import UserProfile, Employee

print("=" * 60)
print("检查 XTCOAI 关联的 UserProfile")
print("=" * 60)

t = Tenant.objects.get(code='XTCOAI')
print(f"\n公司: {t.name} (ID={t.id})")

# 检查 UserProfile
profiles = UserProfile.objects.filter(tenant=t)
print(f"\n关联的 UserProfile ({profiles.count()} 个):")
for profile in profiles:
    print(f"  - 用户: {profile.user.username}, 姓名: {profile.real_name or '-'}")
    
# 询问是否清除
print("\n" + "=" * 60)
response = input("是否清除这些 UserProfile 的公司关联并删除 XTCOAI 公司？(y/n): ")

if response.lower() == 'y':
    # 将 UserProfile 的 tenant 设为 None
    for profile in profiles:
        profile.tenant = None
        profile.save()
        print(f"  ✅ 已清除 {profile.user.username} 的公司关联")
    
    # 检查并清除其他关联数据
    from eims_app.models import Employee
    employees = Employee.objects.filter(tenant=t)
    print(f"\n关联的 Employee 记录: {employees.count()} 个")
    if employees.count() > 0:
        response2 = input("是否删除这些 Employee 记录？(y/n): ")
        if response2.lower() == 'y':
            employees.delete()
            print("  ✅ 已删除 Employee 记录")
    
    # 删除 Tenant
    t.delete()
    print(f"\n✅ 已删除公司: {t.name}")
    
    # 验证
    remaining = Tenant.objects.count()
    print(f"\n当前剩余公司数: {remaining}")
    for tenant in Tenant.objects.all():
        print(f"  - {tenant.name} (ID={tenant.id})")
else:
    print("\n❌ 已取消删除操作")
