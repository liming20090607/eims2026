#!/usr/bin/env python3
"""
检查 XTCOAI 公司关联数据
"""
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')

import django
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserTenantRelation
from eims_app.models import UserProfile

print("=" * 60)
print("检查 XTCOAI 公司关联数据")
print("=" * 60)

t = Tenant.objects.get(code='XTCOAI')
print(f"\n公司: {t.name} (ID={t.id})")

# 检查 UserTenantRelation
utr_count = UserTenantRelation.objects.filter(tenant=t).count()
print(f"\nUserTenantRelation 关联数: {utr_count}")

# 检查 UserProfile  
up_count = UserProfile.objects.filter(tenant=t).count()
print(f"UserProfile 关联数: {up_count}")

# 显示关联用户
if utr_count > 0:
    print("\n关联的用户:")
    relations = UserTenantRelation.objects.filter(tenant=t).select_related('user')
    for rel in relations:
        print(f"  - {rel.user.username} ({rel.user.first_name or rel.user.email})")

print("\n" + "=" * 60)
if utr_count == 0 and up_count == 0:
    print("✅ 无关联数据，可以安全删除")
else:
    print("⚠️  有关联数据，需要先处理关联用户")
print("=" * 60)
