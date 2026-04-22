#!/usr/bin/env python
"""
诊断可视化人员分配页面显示为 0 的问题
"""

import os
import sys
import django

sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db.models import Q
from eims_app.models import Personnel

print("=" * 80)
print("诊断可视化人员分配页面显示为 0 的问题")
print("=" * 80)

# 模拟 allocation_visual 视图的逻辑
tenant_id = 3  # 嘉诚达

print(f"\n【诊断 1】查询 tenant_id={tenant_id} 的所有 Personnel 记录")
personnel_filter = {'is_deleted': False, 'tenant_id': tenant_id}
all_personnel = Personnel.objects.filter(**personnel_filter).order_by('personnel_code')
print(f"  找到 {all_personnel.count()} 条记录")

if all_personnel.count() > 0:
    print("\n【诊断 2】显示所有 Personnel 记录详情：")
    for p in all_personnel:
        print(f"  - {p.personnel_code}: {p.name or 'NULL'}")
        print(f"    department='{p.department or 'NULL'}'")
        print(f"    project={p.project or 'NULL'}")
        print(f"    project2={p.project2 or 'NULL'}")
        print(f"    project3={p.project3 or 'NULL'}")
        print(f"    project4={p.project4 or 'NULL'}")
        print(f"    project5={p.project5 or 'NULL'}")
        print()

print("\n【诊断 3】应用待分配人员过滤器")
unassigned_personnel = all_personnel.filter(
    Q(project__isnull=True) &
    Q(project2__isnull=True) &
    Q(project3__isnull=True) &
    Q(project4__isnull=True) &
    Q(project5__isnull=True) &
    (Q(department__isnull=True) | Q(department='') | Q(department='未分配'))
).order_by('personnel_code')

print(f"  待分配人员数：{unassigned_personnel.count()}")

if unassigned_personnel.count() > 0:
    print("\n【诊断 4】显示待分配人员详情：")
    for p in unassigned_personnel:
        print(f"  ✅ {p.personnel_code}: {p.name or 'NULL'} | department='{p.department or 'NULL'}'")

print("\n【诊断 5】应用部门人员过滤器")
department_personnel = all_personnel.filter(
    department__isnull=False
).exclude(
    department__in=[None, '', '未分配']
).order_by('personnel_code')

print(f"  部门人员数：{department_personnel.count()}")

print("\n" + "=" * 80)
print("诊断完成！")
print("=" * 80)
