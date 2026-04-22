#!/usr/bin/env python
"""
修复项目租户问题 - 将项目改为无租户，让所有用户可见
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_cost_sub_modules import (
    CostProjectInfo,
    CostTaskPlan,
    CostTaskImplementation,
    CostReviewResult,
    CostPaymentStatus,
    CostProjectArchive,
    CostRemunerationDistribution,
)

print("="*60)
print("修复项目租户问题")
print("="*60)

# 找到ID=14的项目
project = CostProjectInfo.objects.get(pk=14)
print(f"\n当前项目信息:")
print(f"  ID: {project.id}")
print(f"  编号: {project.project_code}")
print(f"  名称: {project.project_name}")
print(f"  租户: {project.tenant_id}")

# 修改为无租户
confirm = input("\n是否将该项目改为无租户（所有用户可见）？(y/n): ").strip().lower()
if confirm == 'y':
    old_tenant = project.tenant_id
    project.tenant = None
    project.save()
    
    print(f"\n✓ 项目租户已修改: {old_tenant} → NULL")
    
    # 同步更新子模块
    print("\n同步更新子模块...")
    
    CostTaskPlan.objects.filter(project=project).update(tenant=None)
    print("  ✓ 任务计划")
    
    CostTaskImplementation.objects.filter(project=project).update(tenant=None)
    print("  ✓ 任务实施")
    
    CostReviewResult.objects.filter(project=project).update(tenant=None)
    print("  ✓ 审核成果")
    
    CostPaymentStatus.objects.filter(project=project).update(tenant=None)
    print("  ✓ 收费情况")
    
    CostProjectArchive.objects.filter(project=project).update(tenant=None)
    print("  ✓ 项目存档")
    
    CostRemunerationDistribution.objects.filter(project=project).update(tenant=None)
    print("  ✓ 酬劳分配")
    
    print("\n✅ 修复完成！现在所有租户的用户都能看到这个项目了。")
else:
    print("\n已取消操作")

print("\n" + "="*60)
