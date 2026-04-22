#!/usr/bin/env python
"""
调试项目修改后消失的问题
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_cost_sub_modules import CostProjectInfo

# 检查ID=14的项目
print("="*60)
print("检查项目 ID=14")
print("="*60)

try:
    project = CostProjectInfo.objects.get(pk=14)
    print(f"\n✓ 项目存在:")
    print(f"  ID: {project.id}")
    print(f"  编号: {project.project_code}")
    print(f"  名称: {project.project_name}")
    print(f"  类型: {project.project_type}")
    print(f"  租户: {project.tenant_id}")
    
    # 检查子模块
    print(f"\n检查关联的子模块:")
    from eims_app.models.model_cost_sub_modules import (
        CostTaskPlan, CostTaskImplementation, CostReviewResult,
        CostPaymentStatus, CostProjectArchive, CostRemunerationDistribution
    )
    
    models_info = [
        ("任务计划", CostTaskPlan),
        ("任务实施", CostTaskImplementation),
        ("审核成果", CostReviewResult),
        ("收费情况", CostPaymentStatus),
        ("项目存档", CostProjectArchive),
        ("酬劳分配", CostRemunerationDistribution),
    ]
    
    for name, model in models_info:
        count = model.objects.filter(project=project).count()
        if count > 0:
            record = model.objects.filter(project=project).first()
            print(f"  ✓ {name}: {count}条, 编号={record.project_code}")
        else:
            print(f"  ✗ {name}: 无记录")
    
except CostProjectInfo.DoesNotExist:
    print(f"\n✗ 项目 ID=14 不存在！")
    print("\n可能原因:")
    print("  1. 项目已被删除")
    print("  2. 项目编号修改导致唯一约束冲突，保存失败")
    print("  3. 租户过滤导致看不到该项目")
    
    # 检查是否有编号为"3"的其他项目
    print("\n检查是否有编号='3'的项目:")
    projects_with_code_3 = CostProjectInfo.objects.filter(project_code='3')
    print(f"  找到 {projects_with_code_3.count()} 个项目")
    for p in projects_with_code_3:
        print(f"    ID={p.id}, 编号={p.project_code}, 名称={p.project_name}, 租户={p.tenant_id}")

print("\n" + "="*60)
