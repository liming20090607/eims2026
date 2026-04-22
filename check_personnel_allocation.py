#!/usr/bin/env python
"""检查人员花名册与可视化分配页面的数据关联情况"""

import os
import sys
import django

# 设置 Django 环境
sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel, Department, Employee

print("=" * 80)
print("检查人员花名册与可视化分配页面的数据关联情况")
print("=" * 80)

# 1. 检查 Personnel 表的总体情况
print("\n【1】Personnel 表总体情况：")
print(f"   总记录数（含已删除）：{Personnel.objects.all().count()}")
print(f"   有效记录数（is_deleted=False）：{Personnel.objects.filter(is_deleted=False).count()}")
print(f"   已删除记录数（is_deleted=True）：{Personnel.objects.filter(is_deleted=True).count()}")

# 2. 检查有 tenant_id 的记录
print("\n【2】按 tenant_id 分布：")
tenant_stats = Personnel.objects.filter(is_deleted=False).values('tenant_id').annotate(count=django.db.models.Count('id')).order_by('tenant_id')
for stat in tenant_stats:
    print(f"   tenant_id={stat['tenant_id']}: {stat['count']} 人")

# 3. 检查人员分配状态（可视化页面的分类逻辑）
print("\n【3】人员分配状态（模拟 allocation_visual 视图逻辑）：")

# 获取所有未删除的人员
all_personnel = Personnel.objects.filter(is_deleted=False)

# 待分配人员：所有项目都为空，且部门为空/未分配
from django.db.models import Q
unassigned = all_personnel.filter(
    Q(project__isnull=True) &
    Q(project2__isnull=True) &
    Q(project3__isnull=True) &
    Q(project4__isnull=True) &
    Q(project5__isnull=True) &
    (Q(department__isnull=True) | Q(department='') | Q(department='未分配'))
)
print(f"   待分配人员数：{unassigned.count()}")

# 部门人员：有部门的人员（排除空/未分配）
department_personnel = all_personnel.filter(
    department__isnull=False
).exclude(
    department__in=[None, '', '未分配']
)
print(f"   部门人员数：{department_personnel.count()}")

# 项目人员：有任一项目的人员
project_personnel = all_personnel.filter(
    Q(project__isnull=False) |
    Q(project2__isnull=False) |
    Q(project3__isnull=False) |
    Q(project4__isnull=False) |
    Q(project5__isnull=False)
)
print(f"   项目人员数：{project_personnel.count()}")

# 4. 显示一些示例数据
print("\n【4】待分配人员示例（前5条）：")
unassigned_sample = unassigned[:5]
for p in unassigned_sample:
    print(f"   - {p.personnel_code}: {p.name or 'NULL'} | 部门: '{p.department or 'NULL'}' | 项目: {p.project or 'NULL'}")

print("\n【5】部门人员示例（前5条）：")
dept_sample = department_personnel[:5]
for p in dept_sample:
    print(f"   - {p.personnel_code}: {p.name or 'NULL'} | 部门: '{p.department}' | 项目: {p.project or 'NULL'}")

# 5. 检查 Employee 表
print("\n【6】Employee 表情况：")
print(f"   Employee 总记录数：{Employee.objects.filter(is_deleted=False).count()}")

# 6. 检查 Personnel 和 Employee 的关联
print("\n【7】Personnel 的 employee 字段关联情况：")
with_employee = Personnel.objects.filter(is_deleted=False).exclude(employee__isnull=True).count()
without_employee = Personnel.objects.filter(is_deleted=False, employee__isnull=True).count()
print(f"   已关联 Employee：{with_employee} 人")
print(f"   未关联 Employee：{without_employee} 人")

# 7. 检查部门表
print("\n【8】Department 表情况：")
depts = Department.objects.filter(is_deleted=False)
print(f"   部门总数：{depts.count()}")
for dept in depts[:10]:
    print(f"   - {dept.department_code}: {dept.department_name}")

print("\n" + "=" * 80)
print("诊断完成！")
print("=" * 80)
print("\n【可能的原因】")
print("1. Personnel 记录没有正确的 tenant_id")
print("2. Personnel 记录被标记为 is_deleted=True")
print("3. Personnel 记录的 name 字段为 NULL")
print("4. 部门的 department 字段值不匹配（可能是空字符串而不是 NULL）")
print("5. Personnel 和 Employee 没有正确关联")
