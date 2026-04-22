#!/usr/bin/env python
"""
测试 request.tenant 的设置是否正确
"""

import os
import sys
import django

sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant, Personnel
from django.db.models import Q

print("=" * 80)
print("测试 request.tenant 的设置")
print("=" * 80)

# 1. 检查所有 Tenant
print("\n【1】检查所有 Tenant：")
tenants = Tenant.objects.filter(is_active=True).order_by('id')
for t in tenants:
    print(f"  - ID={t.id}: {t.name} (is_active={t.is_active})")

# 2. 模拟视图中的 tenant_id 过滤
print("\n【2】模拟不同 tenant_id 的查询结果：")

for tenant in tenants:
    print(f"\n  测试 tenant_id={tenant.id} ({tenant.name}):")
    
    personnel_filter = {'is_deleted': False, 'tenant_id': tenant.id}
    all_personnel = Personnel.objects.filter(**personnel_filter).order_by('personnel_code')
    print(f"    总 Personnel 数：{all_personnel.count()}")
    
    # 待分配人员
    unassigned = all_personnel.filter(
        Q(project__isnull=True) &
        Q(project2__isnull=True) &
        Q(project3__isnull=True) &
        Q(project4__isnull=True) &
        Q(project5__isnull=True) &
        (Q(department__isnull=True) | Q(department='') | Q(department='未分配'))
    )
    print(f"    待分配人员：{unassigned.count()}")
    
    # 部门人员
    dept_personnel = all_personnel.filter(
        department__isnull=False
    ).exclude(
        department__in=[None, '', '未分配']
    )
    print(f"    部门人员：{dept_personnel.count()}")
    
    if unassigned.count() > 0:
        print(f"    待分配人员示例：")
        for p in unassigned[:3]:
            print(f"      - {p.personnel_code}: {p.name}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
