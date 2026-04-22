#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从广西鼎策复制10个人员到广西嘉诚达
"""

import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_employee import Employee
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_tenant import Tenant

def copy_personnel():
    """从鼎策复制10个人员到嘉诚达"""
    
    print("=" * 80)
    print("  从广西鼎策复制人员到广西嘉诚达")
    print("=" * 80)
    print()
    
    # 1. 获取两个公司的 Tenant 对象
    try:
        dingce_tenant = Tenant.objects.get(code='dingce')
        jiachengda_tenant = Tenant.objects.get(code='jiachengda')
        print(f"✓ 找到源公司: {dingce_tenant.name} (code: {dingce_tenant.code})")
        print(f"✓ 找到目标公司: {jiachengda_tenant.name} (code: {jiachengda_tenant.code})")
    except Tenant.DoesNotExist as e:
        print(f"✗ 错误: {e}")
        return False
    
    print()
    
    # 2. 从鼎策数据库中查询前10个员工
    print("步骤 1: 从鼎策数据库查询员工...")
    print("-" * 80)
    
    # 使用 using('dingce') 从鼎策数据库查询
    source_employees = Employee.objects.using('dingce').filter(is_deleted=False)[:10]
    
    if not source_employees.exists():
        print("✗ 鼎策数据库中没有员工数据")
        return False
    
    print(f"✓ 找到 {source_employees.count()} 个员工")
    print()
    
    # 3. 复制到嘉诚达数据库
    print("步骤 2: 复制员工到嘉诚达数据库...")
    print("-" * 80)
    
    copied_employees = []
    skipped_employees = []
    
    for emp in source_employees:
        print(f"  处理: {emp.employee_code} - {emp.name}")
        
        # 检查嘉诚达数据库中是否已存在相同 employee_code
        existing = Employee.objects.using('jiachengda').filter(
            employee_code=emp.employee_code
        ).first()
        
        if existing:
            print(f"    ⚠ 跳过 (已存在): {emp.employee_code}")
            skipped_employees.append(emp)
            continue
        
        # 创建新员工记录（修改 tenant 为嘉诚达）
        new_emp = Employee(
            tenant=jiachengda_tenant,
            employee_code=emp.employee_code,
            name=emp.name,
            gender=emp.gender,
            id_card=emp.id_card,
            native_place=emp.native_place,
            ethnic=emp.ethnic,
            education=emp.education,
            address=emp.address,
            home_phone=emp.home_phone,
            mobile=emp.mobile,
            emergency_contact=emp.emergency_contact,
            emergency_phone=emp.emergency_phone,
            wechat=emp.wechat,
            email=emp.email,
            admin_position=emp.admin_position,
            tech_position=emp.tech_position,
            professional_qualification=emp.professional_qualification,
            professional_title=emp.professional_title,
            job_qualification=emp.job_qualification,
            entry_time=emp.entry_time,
            leave_time=emp.leave_time,
            operator='系统复制',
            remark=emp.remark or f'从鼎策复制 (原ID: {emp.id})',
            is_deleted=False,
        )
        
        # 保存到嘉诚达数据库
        try:
            new_emp.save(using='jiachengda')
            print(f"    ✓ 复制成功 (新ID: {new_emp.id})")
            copied_employees.append({
                'source': emp,
                'target': new_emp
            })
        except Exception as e:
            print(f"    ✗ 复制失败: {e}")
    
    print()
    print(f"✓ 复制完成: 成功 {len(copied_employees)} 个, 跳过 {len(skipped_employees)} 个")
    print()
    
    # 4. 复制 Personnel 记录（从鼎策 Personnel 表复制到嘉诚达 Personnel 表）
    print("步骤 4: 复制 Personnel（项目人员花名册）记录...")
    print("-" * 80)
    
    personnel_copied = 0
    personnel_skipped = 0
    
    # 从鼎策 Personnel 表查询前10条记录（用于复制到嘉诚达）
    source_personnel_list = Personnel.objects.using('dingce').filter(is_deleted=False)[:10]
    
    print(f"  找到 {source_personnel_list.count()} 条 Personnel 记录")
    print()
    
    for source_personnel in source_personnel_list:
        # 查找对应的 Employee 记录（从已复制的 Employee 中找）
        matched_employee_id = None
        if source_personnel.employee_id:
            # 尝试通过姓名匹配
            matched_employee = Employee.objects.using('jiachengda').filter(
                name=source_personnel.name,
                is_deleted=False
            ).first()
            if matched_employee:
                matched_employee_id = matched_employee.id
        
        if not matched_employee_id:
            # 如果没找到，尝试通过 personnel_code 匹配 employee_code
            if source_personnel.personnel_code:
                matched_employee = Employee.objects.using('jiachengda').filter(
                    employee_code__contains=source_personnel.personnel_code,
                    is_deleted=False
                ).first()
                if matched_employee:
                    matched_employee_id = matched_employee.id
        
        # 创建新的 Personnel 记录（使用 employee_id 而不是 employee 对象以避免跨数据库关系错误）
        new_personnel = Personnel(
            tenant=jiachengda_tenant,
            employee_id=matched_employee_id,  # 直接使用 ID 避免跨数据库关系错误
            personnel_code=source_personnel.personnel_code,
            name=source_personnel.name,
            gender=source_personnel.gender,
            # 项目字段不复制（因为项目属于不同公司）
            project=None,
            project_code='',
            project2=None,
            project_code2='',
            project3=None,
            project_code3='',
            project4=None,
            project_code4='',
            project5=None,
            project_code5='',
            department=source_personnel.department,
            position=source_personnel.position,
            phone=source_personnel.phone,
            email=source_personnel.email,
            entry_time=source_personnel.entry_time,
            leave_time=source_personnel.leave_time,
            operator='系统复制',
            remark=source_personnel.remark or f'从鼎策复制 (原ID: {source_personnel.id})',
            is_deleted=False,
        )
        
        try:
            new_personnel.save(using='jiachengda')
            personnel_copied += 1
            if matched_employee_id:
                emp = Employee.objects.using('jiachengda').get(id=matched_employee_id)
                print(f"  ✓ Personnel: {new_personnel.personnel_code} | {new_personnel.name} | 关联Employee: {emp.employee_code}")
            else:
                print(f"  ✓ Personnel: {new_personnel.personnel_code} | {new_personnel.name} | 未关联Employee")
        except Exception as e:
            print(f"  ✗ Personnel 复制失败 ({source_personnel.personnel_code}): {e}")
            personnel_skipped += 1
    
    print()
    print(f"✓ Personnel 复制完成: 成功 {personnel_copied} 条, 跳过 {personnel_skipped} 条")
    print()
    
    # 5. 总结
    print("=" * 80)
    print("  复制总结")
    print("=" * 80)
    print(f"✓ 员工复制: {len(copied_employees)} 个成功, {len(skipped_employees)} 个跳过")
    print(f"✓ 项目人员记录复制: {personnel_copied} 条成功, {personnel_skipped} 条跳过")
    print()
    
    if copied_employees:
        print("已复制的员工列表:")
        for emp_mapping in copied_employees:
            source = emp_mapping['source']
            target = emp_mapping['target']
            print(f"  - {source.employee_code} | {source.name} | 新ID: {target.id}")
    
    print()
    print("✅ 复制完成！")
    
    return True

if __name__ == '__main__':
    try:
        success = copy_personnel()
        if success:
            print("\n✅ 所有操作成功完成！")
            sys.exit(0)
        else:
            print("\n✗ 操作失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
