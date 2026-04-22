#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证嘉诚达数据库中的人员数据
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_employee import Employee
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_tenant import Tenant

print("=" * 80)
print("  验证嘉诚达数据库中的人员数据")
print("=" * 80)
print()

# 1. 检查 Tenant
try:
    jiachengda_tenant = Tenant.objects.get(code='jiachengda')
    print(f"✓ 嘉诚达租户: ID={jiachengda_tenant.id}, code={jiachengda_tenant.code}")
except Tenant.DoesNotExist:
    print("✗ 找不到嘉诚达租户")
    sys.exit(1)

print()

# 2. 检查 Employee 表
print("步骤 1: 检查 Employee 表")
print("-" * 80)

jiachengda_employees = Employee.objects.using('jiachengda').filter(is_deleted=False)
print(f"嘉诚达 Employee 总数: {jiachengda_employees.count()}")

if jiachengda_employees.exists():
    print("\n前10个员工:")
    for emp in jiachengda_employees[:10]:
        print(f"  ID={emp.id} | {emp.employee_code} | {emp.name} | tenant_id={emp.tenant_id}")
else:
    print("✗ 嘉诚达 Employee 表中没有数据！")

print()

# 3. 检查 Personnel 表
print("步骤 2: 检查 Personnel 表")
print("-" * 80)

jiachengda_personnel = Personnel.objects.using('jiachengda').filter(is_deleted=False)
print(f"嘉诚达 Personnel 总数: {jiachengda_personnel.count()}")

if jiachengda_personnel.exists():
    print("\n前10个项目人员:")
    for p in jiachengda_personnel[:10]:
        print(f"  ID={p.id} | {p.personnel_code} | {p.name} | employee_id={p.employee_id} | tenant_id={p.tenant_id}")
else:
    print("✗ 嘉诚达 Personnel 表中没有数据！")

print()

# 4. 检查鼎策的数据（对比）
print("步骤 3: 对比鼎策数据")
print("-" * 80)

dingce_employees = Employee.objects.using('dingce').filter(is_deleted=False)
dingce_personnel = Personnel.objects.using('dingce').filter(is_deleted=False)

print(f"鼎策 Employee 总数: {dingce_employees.count()}")
print(f"鼎策 Personnel 总数: {dingce_personnel.count()}")

print()
print("=" * 80)
print("  分析结果")
print("=" * 80)

if jiachengda_employees.exists():
    print("✓ Employee 数据已复制到嘉诚达")
else:
    print("✗ Employee 数据未成功复制到嘉诚达")
    print("  建议: 重新运行 copy_personnel_from_dingce_to_jiachengda.py 脚本")

if jiachengda_personnel.exists():
    print("✓ Personnel 数据已复制到嘉诚达")
else:
    print("ℹ Personnel 数据为空（可能是正常的，如果源数据中也没有 Personnel 记录）")

print()
