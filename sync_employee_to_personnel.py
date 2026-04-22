#!/usr/bin/env python
"""
同步 Employee（员工花名册）到 Personnel（人员去向）
确保所有在职员工都有对应的 Personnel 记录
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee, Personnel, Department

print("=" * 80)
print("同步 Employee（员工花名册）到 Personnel（人员去向）")
print("=" * 80)

# 1. 获取所有在职的 Employee
active_employees = Employee.objects.filter(is_deleted=False)
print(f"\n【步骤 1】在职员工总数：{active_employees.count()} 人")

# 2. 获取所有现有的 Personnel（包括已删除的）
all_personnel = Personnel.objects.all()
print(f"【步骤 2】Personnel 总记录数：{all_personnel.count()} 条")

# 3. 检查哪些 Employee 没有对应的 Personnel 记录
# 通过 name 和 phone 匹配
missing_employees = []
matched_count = 0

for emp in active_employees:
    # 尝试通过手机号或姓名匹配
    matched_personnel = Personnel.objects.filter(
        is_deleted=False,
        employee=emp
    ).first()
    
    if not matched_personnel:
        # 尝试通过姓名和手机号匹配
        matched_personnel = Personnel.objects.filter(
            name=emp.name,
            phone=emp.mobile
        ).exclude(is_deleted=True).first()
    
    if matched_personnel:
        matched_count += 1
    else:
        missing_employees.append(emp)

print(f"【步骤 3】已关联 Personnel 的员工：{matched_count} 人")
print(f"【步骤 4】缺少 Personnel 记录的员工：{len(missing_employees)} 人")

# 4. 创建缺失的 Personnel 记录
if missing_employees:
    print(f"\n{'=' * 80}")
    print(f"开始创建 {len(missing_employees)} 条 Personnel 记录...")
    print(f"{'=' * 80}\n")
    
    created_count = 0
    skipped_count = 0
    
    for emp in missing_employees:
        try:
            # 检查是否已存在（避免重复创建）
            existing = Personnel.objects.filter(
                employee=emp,
                is_deleted=False
            ).first()
            
            if existing:
                skipped_count += 1
                print(f"  ⚠️  跳过 {emp.employee_code}: {emp.name}（已存在）")
                continue
            
            # 生成人员编号
            # 根据租户生成不同的编号前缀
            tenant_id = emp.tenant_id if emp.tenant_id else 0
            
            if tenant_id == 1:  # 鼎策
                prefix = "DCRY"
            elif tenant_id == 2:  # 升昌
                prefix = "SCRY"
            elif tenant_id == 3:  # 嘉诚达
                prefix = "JCDRY"
            else:
                prefix = "RY"
            
            # 获取当前最大的编号
            max_code = Personnel.objects.filter(
                personnel_code__startswith=prefix
            ).order_by('-personnel_code').first()
            
            if max_code:
                # 提取数字部分
                try:
                    num_part = int(max_code.personnel_code.replace(prefix + '-', ''))
                    new_num = num_part + 1
                except:
                    new_num = Personnel.objects.filter(
                        personnel_code__startswith=prefix
                    ).count() + 1
            else:
                new_num = 1
            
            personnel_code = f"{prefix}-{new_num:03d}"
            
            # 创建 Personnel 记录
            personnel = Personnel.objects.create(
                employee=emp,
                personnel_code=personnel_code,
                name=emp.name,
                gender=emp.gender,
                phone=emp.mobile,
                email=emp.email,
                department='',  # 待分配
                position='',
                tenant=emp.tenant,
                is_deleted=False,
                operator='系统同步',
                remark='从 Employee 表自动同步'
            )
            
            created_count += 1
            print(f"  ✅ {personnel_code}: {emp.name} (tenant_id={tenant_id}, 部门: 待分配)")
            
        except Exception as e:
            print(f"  ❌ {emp.employee_code}: {emp.name} - 创建失败: {str(e)}")
            skipped_count += 1
    
    print(f"\n{'=' * 80}")
    print(f"同步完成！")
    print(f"  ✅ 成功创建：{created_count} 条")
    print(f"  ⚠️  跳过：{skipped_count} 条")
    print(f"{'=' * 80}")
else:
    print("\n✅ 所有员工都已有 Personnel 记录，无需同步！")

# 5. 验证同步结果
print("\n【验证】同步后 Personnel 统计：")
print(f"  有效 Personnel 记录数：{Personnel.objects.filter(is_deleted=False).count()}")
print(f"  按 tenant_id 分布：")

from django.db.models import Count
tenant_stats = Personnel.objects.filter(is_deleted=False).values('tenant_id').annotate(count=Count('id')).order_by('tenant_id')
for stat in tenant_stats:
    print(f"    tenant_id={stat['tenant_id']}: {stat['count']} 人")

print("\n" + "=" * 80)
