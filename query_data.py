#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询截止到昨晚的数据统计（即所有历史数据）
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
from django.utils import timezone
from django.contrib.auth.models import User

# 获取今天凌晨的时间点（即昨晚24:00）
today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

print("=" * 60)
print("数据统计（截止到昨晚 - 所有历史数据）")
print("=" * 60)
print(f"\n查询时间点: {today.strftime('%Y-%m-%d %H:%M:%S')} 之前的所有数据")
print("=" * 60)

# 合同数据
print("\n【合同数据】")
contracts = Contract.objects.all()
print(f"合同总数: {contracts.count()}")
if contracts.exists():
    print("\n最近10条合同:")
    for c in contracts.order_by('-update_time')[:10]:
        update_time = c.update_time.strftime("%Y-%m-%d %H:%M") if c.update_time else "无"
        create_time = c.create_time.strftime("%Y-%m-%d %H:%M") if c.create_time else "无"
        print(f"  - {c.contract_name} ({c.contract_code})")
        print(f"    状态: {c.get_status_display()} | 类型: {c.get_contract_type_display()}")
        print(f"    创建: {create_time} | 更新: {update_time}")

# 项目数据
print("\n【项目数据】")
projects = ProjectDetail.objects.all()
print(f"项目总数: {projects.count()}")
if projects.exists():
    print("\n最近10条项目:")
    for p in projects.order_by('-updated_at')[:10]:
        update_time = p.updated_at.strftime("%Y-%m-%d %H:%M") if p.updated_at else "无"
        create_time = p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "无"
        print(f"  - {p.project_name} ({p.project_code})")
        print(f"    状态: {p.get_project_status_display() if hasattr(p, 'get_project_status_display') else 'N/A'}")
        print(f"    创建: {create_time} | 更新: {update_time}")

# 员工数据
print("\n【员工数据】")
employees = Employee.objects.all()
print(f"员工总数: {employees.count()}")
if employees.exists():
    print("\n最近10条员工:")
    for e in employees.order_by('-update_time')[:10]:
        update_time = e.update_time.strftime("%Y-%m-%d %H:%M") if e.update_time else "无"
        create_time = e.create_time.strftime("%Y-%m-%d %H:%M") if e.create_time else "无"
        admin_pos = e.admin_position or "未设置"
        tech_pos = e.tech_position or "未设置"
        print(f"  - {e.name} (编号: {e.employee_code})")
        print(f"    行政职务: {admin_pos} | 技术职务: {tech_pos}")
        print(f"    手机: {e.mobile} | 入职: {e.entry_time.strftime('%Y-%m-%d') if e.entry_time else '未设置'}")
        print(f"    创建: {create_time} | 更新: {update_time}")

# 人员数据
print("\n【人员数据】")
personnels = Personnel.objects.all()
print(f"人员总数: {personnels.count()}")
if personnels.exists():
    print("\n最近10条人员:")
    for p in personnels.order_by('-update_time')[:10]:
        update_time = p.update_time.strftime("%Y-%m-%d %H:%M") if p.update_time else "无"
        create_time = p.create_time.strftime("%Y-%m-%d %H:%M") if p.create_time else "无"
        project_name = p.project.project_name if p.project else "未分配"
        print(f"  - {p.name} (编号: {p.personnel_code})")
        print(f"    主要项目: {project_name} | 部门: {p.department or '未分配'}")
        print(f"    创建: {create_time} | 更新: {update_time}")
else:
    print("  （暂无人员数据）")

# 用户数据
print("\n【用户数据】")
users = UserProfile.objects.all()
print(f"用户总数: {users.count()}")
if users.exists():
    print("\n最近10条用户:")
    for u in users.order_by('-user__date_joined')[:10]:
        join_time = u.user.date_joined.strftime("%Y-%m-%d %H:%M")
        full_name = u.real_name or "无姓名"
        is_staff = "管理员" if u.user.is_staff else ("超级管理员" if u.user.is_superuser else "普通用户")
        tenant_name = u.tenant.name if u.tenant else "未分配"
        print(f"  - {u.user.username} ({full_name})")
        print(f"    角色: {is_staff} | 公司: {tenant_name}")
        print(f"    注册时间: {join_time}")

print("\n" + "=" * 60)
print("数据加载完成！")
print("=" * 60)
