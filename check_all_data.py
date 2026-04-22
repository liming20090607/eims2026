#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中所有历史数据（包括所有租户）
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_contract import Contract
from eims_app.models.model_project_detail import ProjectDetail
from eims_app.models.model_employee import Employee
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_user import UserProfile
from eims_app.models.model_tenant import Tenant
from django.contrib.auth.models import User

print("=" * 80)
print("数据库完整数据统计（包含所有租户的历史数据）")
print("=" * 80)

# 检查租户
print("\n【租户信息】")
tenants = Tenant.objects.all()
print(f"租户总数: {tenants.count()}")
for t in tenants:
    print(f"  - ID:{t.id} | {t.name} (代码: {t.code})")

# 检查合同（按租户分组）
print("\n【合同数据 - 按租户统计】")
all_contracts = Contract.objects.all()
print(f"合同总数（所有租户）: {all_contracts.count()}")

# 按租户统计
for tenant in tenants:
    tenant_contracts = Contract.objects.filter(tenant=tenant)
    print(f"\n  租户: {tenant.name}")
    print(f"  合同数: {tenant_contracts.count()}")
    if tenant_contracts.exists():
        for c in tenant_contracts.order_by('-update_time')[:5]:
            print(f"    - {c.contract_name} ({c.contract_code}) | 状态: {c.get_status_display()}")
            print(f"      创建: {c.create_time.strftime('%Y-%m-%d %H:%M')}")

# 检查无租户的合同
no_tenant_contracts = Contract.objects.filter(tenant__isnull=True)
if no_tenant_contracts.exists():
    print(f"\n  未分配租户的合同: {no_tenant_contracts.count()}条")
    for c in no_tenant_contracts[:5]:
        print(f"    - {c.contract_name} ({c.contract_code})")

# 检查项目（按租户分组）
print("\n【项目数据 - 按租户统计】")
all_projects = ProjectDetail.objects.all()
print(f"项目总数（所有租户）: {all_projects.count()}")

for tenant in tenants:
    tenant_projects = ProjectDetail.objects.filter(tenant=tenant)
    print(f"\n  租户: {tenant.name}")
    print(f"  项目数: {tenant_projects.count()}")
    if tenant_projects.exists():
        for p in tenant_projects.order_by('-updated_at')[:5]:
            status_display = p.get_project_status_display() if hasattr(p, 'get_project_status_display') else p.project_status
            print(f"    - {p.project_name} ({p.project_code}) | 状态: {status_display}")
            print(f"      创建: {p.created_at.strftime('%Y-%m-%d %H:%M')}")

# 检查无租户的项目
no_tenant_projects = ProjectDetail.objects.filter(tenant__isnull=True)
if no_tenant_projects.exists():
    print(f"\n  未分配租户的项目: {no_tenant_projects.count()}条")
    for p in no_tenant_projects[:5]:
        print(f"    - {p.project_name} ({p.project_code})")

# 检查员工（按租户分组）
print("\n【员工数据 - 按租户统计】")
all_employees = Employee.objects.all()
print(f"员工总数（所有租户）: {all_employees.count()}")

for tenant in tenants:
    tenant_employees = Employee.objects.filter(tenant=tenant)
    print(f"\n  租户: {tenant.name}")
    print(f"  员工数: {tenant_employees.count()}")
    if tenant_employees.exists():
        for e in tenant_employees.order_by('-update_time')[:5]:
            print(f"    - {e.name} (编号: {e.employee_code})")
            print(f"      手机: {e.mobile} | 入职: {e.entry_time.strftime('%Y-%m-%d') if e.entry_time else '未设置'}")

# 检查无租户的员工
no_tenant_employees = Employee.objects.filter(tenant__isnull=True)
if no_tenant_employees.exists():
    print(f"\n  未分配租户的员工: {no_tenant_employees.count()}条")
    for e in no_tenant_employees[:5]:
        print(f"    - {e.name} (编号: {e.employee_code})")

# 检查人员（按租户分组）
print("\n【人员数据 - 按租户统计】")
all_personnels = Personnel.objects.all()
print(f"人员总数（所有租户）: {all_personnels.count()}")

for tenant in tenants:
    tenant_personnels = Personnel.objects.filter(tenant=tenant)
    print(f"\n  租户: {tenant.name}")
    print(f"  人员数: {tenant_personnels.count()}")
    if tenant_personnels.exists():
        for p in tenant_personnels.order_by('-update_time')[:5]:
            project_name = p.project.project_name if p.project else "未分配"
            print(f"    - {p.name} (编号: {p.personnel_code})")
            print(f"      主要项目: {project_name} | 部门: {p.department or '未分配'}")

# 检查无租户的人员
no_tenant_personnels = Personnel.objects.filter(tenant__isnull=True)
if no_tenant_personnels.exists():
    print(f"\n  未分配租户的人员: {no_tenant_personnels.count()}条")
    for p in no_tenant_personnels[:5]:
        print(f"    - {p.name} (编号: {p.personnel_code})")

# 用户统计
print("\n【用户数据】")
all_users = User.objects.all()
print(f"用户总数: {all_users.count()}")
admin_users = all_users.filter(is_staff=True)
super_users = all_users.filter(is_superuser=True)
normal_users = all_users.filter(is_staff=False, is_superuser=False)
print(f"  - 管理员 (is_staff): {admin_users.count()}")
print(f"  - 超级管理员 (is_superuser): {super_users.count()}")
print(f"  - 普通用户: {normal_users.count()}")

print("\n" + "=" * 80)
print("数据检查完成！")
print("=" * 80)
