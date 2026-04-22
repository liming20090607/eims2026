#!/usr/bin/env python
"""
测试自动创建子模块记录功能

使用方法:
    python test_auto_create.py
"""

import os
import sys
import django

# 设置Django环境
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


def test_auto_create():
    """测试自动创建子模块记录"""
    print("="*60)
    print("测试：自动创建子模块记录")
    print("="*60)
    
    # 1. 统计当前各表记录数
    print("\n【步骤1】统计当前记录数...")
    models_info = [
        ("项目信息", CostProjectInfo),
        ("任务计划", CostTaskPlan),
        ("任务实施", CostTaskImplementation),
        ("审核成果", CostReviewResult),
        ("收费情况", CostPaymentStatus),
        ("项目存档", CostProjectArchive),
        ("酬劳分配", CostRemunerationDistribution),
    ]
    
    before_counts = {}
    for name, model in models_info:
        count = model.objects.count()
        before_counts[name] = count
        print(f"  {name}: {count} 条")
    
    # 2. 创建一个新的项目信息记录
    print("\n【步骤2】创建新的项目信息记录...")
    try:
        new_project = CostProjectInfo.objects.create(
            project_code=f"TEST_{CostProjectInfo.objects.count() + 1:03d}",
            project_name="自动创建测试项目",
            project_type='budget',
            client_unit="测试建设单位",
            compilation_amount=100000.00,
        )
        print(f"  ✓ 创建成功: {new_project.project_code} - {new_project.project_name}")
    except Exception as e:
        print(f"  ✗ 创建失败: {e}")
        return
    
    # 3. 检查是否自动创建了子模块记录
    print("\n【步骤3】检查子模块记录...")
    after_counts = {}
    for name, model in models_info:
        count = model.objects.count()
        after_counts[name] = count
        diff = count - before_counts[name]
        status = "✓" if diff > 0 else "✗"
        print(f"  {status} {name}: {before_counts[name]} → {count} (增加 {diff} 条)")
    
    # 4. 验证外键关联
    print("\n【步骤4】验证外键关联...")
    try:
        task_plan = CostTaskPlan.objects.filter(project=new_project).first()
        if task_plan:
            print(f"  ✓ 任务计划已关联: project_id={task_plan.project_id}")
        else:
            print(f"  ✗ 任务计划未找到关联")
        
        task_impl = CostTaskImplementation.objects.filter(project=new_project).first()
        if task_impl:
            print(f"  ✓ 任务实施已关联: project_id={task_impl.project_id}")
        else:
            print(f"  ✗ 任务实施未找到关联")
        
        review = CostReviewResult.objects.filter(project=new_project).first()
        if review:
            print(f"  ✓ 审核成果已关联: project_id={review.project_id}")
        else:
            print(f"  ✗ 审核成果未找到关联")
        
        payment = CostPaymentStatus.objects.filter(project=new_project).first()
        if payment:
            print(f"  ✓ 收费情况已关联: project_id={payment.project_id}")
        else:
            print(f"  ✗ 收费情况未找到关联")
        
        archive = CostProjectArchive.objects.filter(project=new_project).first()
        if archive:
            print(f"  ✓ 项目存档已关联: project_id={archive.project_id}")
        else:
            print(f"  ✗ 项目存档未找到关联")
        
        remuneration = CostRemunerationDistribution.objects.filter(project=new_project).first()
        if remuneration:
            print(f"  ✓ 酬劳分配已关联: project_id={remuneration.project_id}")
        else:
            print(f"  ✗ 酬劳分配未找到关联")
        
    except Exception as e:
        print(f"  ✗ 验证失败: {e}")
    
    # 5. 清理测试数据（可选）
    print("\n【步骤5】清理测试数据...")
    confirm = input("  是否删除测试项目及其子模块记录？(y/n): ").strip().lower()
    if confirm == 'y':
        try:
            # Django的CASCADE会自动删除关联的子模块记录
            deleted_count, _ = new_project.delete()
            print(f"  ✓ 已删除测试项目及 {deleted_count-1} 条关联记录")
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")
    else:
        print(f"  ℹ 保留测试数据，项目编号: {new_project.project_code}")
    
    # 6. 总结
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    
    # 检查是否所有子模块都自动创建了
    all_created = all(after_counts[name] > before_counts[name] for name, _ in models_info[1:])
    if all_created:
        print("✅ 所有子模块记录都已自动创建！")
    else:
        print("⚠️  部分子模块记录未自动创建，请检查日志")


if __name__ == '__main__':
    test_auto_create()
