#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从4月6日备份恢复项目、人员、员工数据到当前多租户数据库
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_project_detail import ProjectDetail
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_employee import Employee
from eims_app.models.model_tenant import Tenant
from django.contrib.auth.models import User
from django.utils import timezone

backup_file = 'backup_local_20260406_172503.json'

print("=" * 80)
print("从4月6日备份恢复数据")
print("=" * 80)
print(f"\n备份文件: {backup_file}")

# 加载备份数据
with open(backup_file, 'r', encoding='utf-8') as f:
    backup_data = json.load(f)

print(f"备份总记录数: {len(backup_data)}")

# 获取默认租户（广西鼎策）
default_tenant = Tenant.objects.filter(code='dingce').first()
if not default_tenant:
    print("\n⚠ 警告: 未找到默认租户，将使用第一个可用租户")
    default_tenant = Tenant.objects.first()

print(f"\n使用的租户: {default_tenant.name if default_tenant else '无'} (ID: {default_tenant.id if default_tenant else 'N/A'})")

# 统计备份中的数据
project_data = [item for item in backup_data if item['model'] == 'eims_app.projectdetail']
personnel_data = [item for item in backup_data if item['model'] == 'eims_app.personnel']
employee_data = [item for item in backup_data if item['model'] == 'eims_app.employee']

print(f"\n备份中的数据:")
print(f"  - 项目: {len(project_data)} 条")
print(f"  - 人员: {len(personnel_data)} 条")
print(f"  - 员工: {len(employee_data)} 条")

# 检查当前数据库中的数据
current_projects = ProjectDetail.objects.count()
current_personnels = Personnel.objects.count()
current_employees = Employee.objects.count()

print(f"\n当前数据库中的数据:")
print(f"  - 项目: {current_projects} 条")
print(f"  - 人员: {current_personnels} 条")
print(f"  - 员工: {current_employees} 条")

print("\n" + "=" * 80)
print("开始恢复数据...")
print("=" * 80)

# 恢复员工数据
print("\n【1/3】恢复员工数据...")
employee_count = 0
for item in employee_data:
    fields = item['fields']
    
    # 检查是否已存在
    if Employee.objects.filter(employee_code=fields.get('employee_code')).exists():
        print(f"  ⊘ 跳过已存在的员工: {fields.get('name')} ({fields.get('employee_code')})")
        continue
    
    try:
        emp = Employee(
            tenant=default_tenant,
            employee_code=fields.get('employee_code', ''),
            name=fields.get('name', ''),
            gender=fields.get('gender', 0),
            id_card=fields.get('id_card', ''),
            native_place=fields.get('native_place', ''),
            ethnic=fields.get('ethnic', 'han'),
            education=fields.get('education', 'bachelor'),
            address=fields.get('address', ''),
            home_phone=fields.get('home_phone', ''),
            mobile=fields.get('mobile', ''),
            emergency_contact=fields.get('emergency_contact', ''),
            emergency_phone=fields.get('emergency_phone', ''),
            wechat=fields.get('wechat', ''),
            email=fields.get('email', ''),
            admin_position=fields.get('admin_position', ''),
            tech_position=fields.get('tech_position', ''),
            professional_qualification=fields.get('professional_qualification', ''),
            professional_title=fields.get('professional_title', ''),
            job_qualification=fields.get('job_qualification', ''),
            entry_time=fields.get('entry_time'),
            leave_time=fields.get('leave_time'),
            operator=fields.get('operator', ''),
            remark=fields.get('remark', ''),
            is_deleted=fields.get('is_deleted', False),
        )
        
        # 设置创建和更新时间
        if fields.get('create_time'):
            emp.create_time = timezone.datetime.fromisoformat(fields['create_time'].replace('Z', '+00:00'))
        if fields.get('update_time'):
            emp.update_time = timezone.datetime.fromisoformat(fields['update_time'].replace('Z', '+00:00'))
        
        emp.save()
        employee_count += 1
        print(f"  ✓ 恢复员工: {emp.name} ({emp.employee_code})")
    except Exception as e:
        print(f"  ✗ 恢复员工失败: {fields.get('name')} - {e}")

print(f"\n✓ 员工恢复完成: {employee_count} 条")

# 恢复项目数据
print("\n【2/3】恢复项目数据...")
project_count = 0
for item in project_data:
    fields = item['fields']
    
    # 检查是否已存在
    if ProjectDetail.objects.filter(project_code=fields.get('project_code')).exists():
        print(f"  ⊘ 跳过已存在的项目: {fields.get('project_name')} ({fields.get('project_code')})")
        continue
    
    try:
        proj = ProjectDetail(
            tenant=default_tenant,
            project_code=fields.get('project_code', ''),
            contract_code=fields.get('contract_code', ''),
            project_name=fields.get('project_name', ''),
            project_status=fields.get('project_status', 'not_started'),
            contract_status=fields.get('contract_status', 'pending_review'),
            settlement_status=fields.get('settlement_status', 'unsettled'),
            contract_party_a=fields.get('contract_party_a', fields.get('client_name', '')),
            contract_party_b=fields.get('contract_party_b', ''),
            signing_date=fields.get('signing_date') or fields.get('signing_time'),
            contract_amount=fields.get('contract_amount', 0),
            payment_agreement=fields.get('payment_agreement', ''),
            cumulative_payment=fields.get('cumulative_payment', 0),
            contract_balance=fields.get('contract_balance', 0),
            project_scale=fields.get('project_scale', ''),
            project_investment=fields.get('project_investment'),
            project_address=fields.get('project_address', ''),
            agreed_staffing=fields.get('agreed_staffing', ''),
            service_start_date=fields.get('service_start_date') or fields.get('start_date'),
            service_period_months=fields.get('service_period_months', 0),
            service_deadline=fields.get('service_deadline') or fields.get('planned_end_date'),
            extension_agreement=fields.get('extension_agreement', ''),
            actual_extension_status=fields.get('actual_extension_status', ''),
            construction_permit_status=fields.get('construction_permit_status', ''),
            entry_notice=fields.get('entry_notice', 'no'),
            entry_time=fields.get('entry_time'),
            planned_start_date=fields.get('planned_start_date') or fields.get('planned_start_time'),
            actual_start_date=fields.get('actual_start_date'),
            estimated_completion_date=fields.get('estimated_completion_date') or fields.get('estimated_completion_time'),
            project_director=fields.get('project_director', ''),
            project_manager=fields.get('project_manager', ''),
            contact_phone=fields.get('contact_phone', fields.get('client_phone', '')),
            remark=fields.get('remark', ''),
        )
        
        # 设置创建和更新时间
        if fields.get('created_at'):
            proj.created_at = timezone.datetime.fromisoformat(fields['created_at'].replace('Z', '+00:00'))
        if fields.get('updated_at'):
            proj.updated_at = timezone.datetime.fromisoformat(fields['updated_at'].replace('Z', '+00:00'))
        
        proj.save()
        project_count += 1
        print(f"  ✓ 恢复项目: {proj.project_name} ({proj.project_code})")
    except Exception as e:
        print(f"  ✗ 恢复项目失败: {fields.get('project_name')} - {e}")

print(f"\n✓ 项目恢复完成: {project_count} 条")

# 恢复人员数据
print("\n【3/3】恢复人员数据...")
personnel_count = 0

# 先建立员工编号到ID的映射
employee_map = {}
for emp in Employee.objects.all():
    employee_map[emp.employee_code] = emp.id

# 建立项目编号到ID的映射
project_map = {}
for proj in ProjectDetail.objects.all():
    project_map[proj.project_code] = proj.id

for item in personnel_data:
    fields = item['fields']
    
    # 检查是否已存在
    if Personnel.objects.filter(personnel_code=fields.get('personnel_code')).exists():
        print(f"  ⊘ 跳过已存在的人员: {fields.get('name')} ({fields.get('personnel_code')})")
        continue
    
    try:
        # 查找关联的员工
        employee_id = None
        emp_code = fields.get('employee_code', '')
        if emp_code and emp_code in employee_map:
            employee_id = employee_map[emp_code]
        
        # 查找关联的项目
        project_id = None
        proj_code = fields.get('project_code', '')
        if proj_code and proj_code in project_map:
            project_id = project_map[proj_code]
        
        pers = Personnel(
            tenant=default_tenant,
            employee_id=employee_id,
            personnel_code=fields.get('personnel_code', ''),
            name=fields.get('name', ''),
            gender=fields.get('gender', 0),
            project_id=project_id,
            project_code=proj_code,
            department=fields.get('department', ''),
            position=fields.get('position', ''),
            phone=fields.get('phone', ''),
            email=fields.get('email', ''),
            entry_time=fields.get('entry_time'),
            leave_time=fields.get('leave_time'),
            operator=fields.get('operator', ''),
            remark=fields.get('remark', ''),
            is_deleted=fields.get('is_deleted', False),
        )
        
        # 设置创建和更新时间
        if fields.get('create_time'):
            pers.create_time = timezone.datetime.fromisoformat(fields['create_time'].replace('Z', '+00:00'))
        if fields.get('update_time'):
            pers.update_time = timezone.datetime.fromisoformat(fields['update_time'].replace('Z', '+00:00'))
        
        pers.save()
        personnel_count += 1
        print(f"  ✓ 恢复人员: {pers.name} ({pers.personnel_code}) - 项目: {proj_code or '未分配'}")
    except Exception as e:
        print(f"  ✗ 恢复人员失败: {fields.get('name')} - {e}")

print(f"\n✓ 人员恢复完成: {personnel_count} 条")

# 最终统计
print("\n" + "=" * 80)
print("数据恢复完成！最终统计:")
print("=" * 80)
print(f"\n员工总数: {Employee.objects.count()} (新增: {employee_count})")
print(f"项目总数: {ProjectDetail.objects.count()} (新增: {project_count})")
print(f"人员总数: {Personnel.objects.count()} (新增: {personnel_count})")

print("\n" + "=" * 80)
print("✓ 所有数据恢复成功！")
print("=" * 80)
