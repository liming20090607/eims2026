#!/usr/bin/env python3
"""
自动删除 XTCOAI 公司及其关联数据
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
print("自动删除 XTCOAI 公司")
print("=" * 60)

t = Tenant.objects.get(code='XTCOAI')
print(f"\n公司: {t.name} (ID={t.id})")

# 清除 UserProfile 的公司关联
profiles = UserProfile.objects.filter(tenant=t)
print(f"\n清除 UserProfile 关联 ({profiles.count()} 个):")
for profile in profiles:
    profile.tenant = None
    profile.save()
    print(f"  ✅ {profile.user.username}")

# 删除 Employee 记录
employees = Employee.objects.filter(tenant=t)
print(f"\n删除 Employee 记录 ({employees.count()} 个)")
employees.delete()

# 删除 Tenant
t.delete()
print(f"\n✅ 已删除公司: 协同AI办公系统")

# 验证剩余公司
print("\n" + "=" * 60)
print("剩余公司列表:")
print("=" * 60)
tenants = Tenant.objects.all()
print(f"总数: {tenants.count()}")
for tenant in tenants:
    print(f"  ID={tenant.id}, {tenant.name}")

print("\n✅ 完成！")
