#!/usr/bin/env python
"""
测试修改项目信息后同步子模块冗余字段功能

使用方法:
    python test_sync_update.py
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


def test_sync_on_update():
    """测试修改项目信息后同步子模块"""
    print("="*60)
    print("测试：修改项目信息后同步子模块冗余字段")
    print("="*60)
    
    # 1. 找到一个现有的项目进行测试
    print("\n【步骤1】查找测试项目...")
    project = CostProjectInfo.objects.filter(project_code__startswith='TEST_').first()
    
    if not project:
        # 如果没有TEST项目，创建一个
        print("  未找到TEST项目，创建新项目...")
        project = CostProjectInfo.objects.create(
            project_code=f"TEST_SYNC_{CostProjectInfo.objects.count() + 1:03d}",
            project_name="同步测试项目",
            project_type='budget',
        )
        print(f"  ✓ 创建成功: {project.project_code}")
    
    print(f"  找到项目: {project.project_code} - {project.project_name}")
    
    # 2. 记录修改前的子模块数据
    print("\n【步骤2】记录修改前的子模块数据...")
    before_data = {}
    
    models_info = [
        ("任务计划", CostTaskPlan),
        ("任务实施", CostTaskImplementation),
        ("审核成果", CostReviewResult),
        ("收费情况", CostPaymentStatus),
        ("项目存档", CostProjectArchive),
        ("酬劳分配", CostRemunerationDistribution),
    ]
    
    for name, model in models_info:
        records = model.objects.filter(project=project)
        if records.exists():
            record = records.first()
            before_data[name] = {
                'project_code': record.project_code,
                'project_name': record.project_name,
                'project_type': record.project_type,
            }
            print(f"  ✓ {name}: {record.project_code} | {record.project_name}")
        else:
            print(f"  ✗ {name}: 无记录")
    
    # 3. 修改项目信息
    print("\n【步骤3】修改项目信息...")
    old_code = project.project_code
    old_name = project.project_name
    
    new_code = f"{old_code}_MODIFIED"
    new_name = f"{old_name}（已修改）"
    
    print(f"  项目编号: {old_code} → {new_code}")
    print(f"  项目名称: {old_name} → {new_name}")
    
    project.project_code = new_code
    project.project_name = new_name
    project.save()
    
    print(f"  ✓ 保存成功")
    
    # 4. 检查子模块是否同步更新
    print("\n【步骤4】检查子模块同步情况...")
    all_synced = True
    
    for name, model in models_info:
        records = model.objects.filter(project=project)
        if records.exists():
            record = records.first()
            is_synced = (
                record.project_code == new_code and
                record.project_name == new_name
            )
            
            status = "✓" if is_synced else "✗"
            print(f"  {status} {name}:")
            print(f"      编号: {record.project_code} {'(已同步)' if record.project_code == new_code else '(未同步!)'}")
            print(f"      名称: {record.project_name} {'(已同步)' if record.project_name == new_name else '(未同步!)'}")
            
            if not is_synced:
                all_synced = False
        else:
            print(f"  ✗ {name}: 无记录")
            all_synced = False
    
    # 5. 验证主表数据
    print("\n【步骤5】验证主表数据...")
    project.refresh_from_db()
    print(f"  项目编号: {project.project_code}")
    print(f"  项目名称: {project.project_name}")
    
    # 6. 恢复原始数据（可选）
    print("\n【步骤6】恢复原始数据...")
    confirm = input("  是否恢复原始项目编号和名称？(y/n): ").strip().lower()
    if confirm == 'y':
        project.project_code = old_code
        project.project_name = old_name
        project.save()
        print(f"  ✓ 已恢复: {old_code} - {old_name}")
        
        # 再次验证同步
        print("\n【步骤7】验证恢复后的同步...")
        for name, model in models_info:
            records = model.objects.filter(project=project)
            if records.exists():
                record = records.first()
                is_restored = (
                    record.project_code == old_code and
                    record.project_name == old_name
                )
                status = "✓" if is_restored else "✗"
                print(f"  {status} {name}: {record.project_code}")
    else:
        print(f"  ℹ 保留修改后的数据: {new_code}")
    
    # 8. 总结
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    
    if all_synced:
        print("✅ 所有子模块冗余字段都已同步更新！")
    else:
        print("⚠️  部分子模块未同步，请检查日志")


if __name__ == '__main__':
    test_sync_on_update()
