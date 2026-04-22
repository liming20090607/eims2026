#!/usr/bin/env python
"""
修复租户 ID 映射并重新同步数据
"""

import os
import sys
import django

sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant, Personnel, Employee

print("=" * 80)
print("修复租户 ID 映射并重新同步数据")
print("=" * 80)

# 1. 显示正确的租户映射
print("\n【1】当前租户信息：")
tenants = Tenant.objects.filter(is_active=True).order_by('id')
tenant_map = {}
for t in tenants:
    tenant_map[t.id] = t.name
    print(f"  tenant_id={t.id}: {t.name}")

# 2. 检查 Personnel 的 tenant_id 分布
print("\n【2】当前 Personnel 的 tenant_id 分布：")
from django.db.models import Count
stats = Personnel.objects.filter(is_deleted=False).values('tenant_id').annotate(count=Count('id'))
for s in stats:
    tid = s['tenant_id']
    tname = tenant_map.get(tid, '未知')
    print(f"  tenant_id={tid} ({tname}): {s['count']} 人")

# 3. 检查 Employee 的 tenant_id 分布
print("\n【3】当前 Employee 的 tenant_id 分布：")
emp_stats = Employee.objects.filter(is_deleted=False).values('tenant_id').annotate(count=Count('id'))
for s in emp_stats:
    tid = s['tenant_id']
    tname = tenant_map.get(tid, '未知')
    print(f"  tenant_id={tid} ({tname}): {s['count']} 人")

# 4. 检查嘉诚达的具体数据
print("\n【4】嘉诚达（假设 tenant_id=4）的数据：")
jcd_tenants = [t for t in tenants if '嘉诚达' in t.name]
if jcd_tenants:
    jcd_tenant = jcd_tenants[0]
    print(f"  嘉诚达 tenant_id={jcd_tenant.id}")
    
    # Personnel
    jcd_personnel = Personnel.objects.filter(is_deleted=False, tenant_id=jcd_tenant.id)
    print(f"  Personnel 记录数：{jcd_personnel.count()}")
    for p in jcd_personnel:
        print(f"    - {p.personnel_code}: {p.name}")
    
    # Employee
    jcd_employee = Employee.objects.filter(is_deleted=False, tenant_id=jcd_tenant.id)
    print(f"  Employee 记录数：{jcd_employee.count()}")
else:
    print("  ⚠️  未找到包含'嘉诚达'的租户")

print("\n" + "=" * 80)
print("诊断完成！")
print("=" * 80)
