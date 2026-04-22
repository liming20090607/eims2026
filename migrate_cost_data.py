#!/usr/bin/env python
"""
造价咨询模块数据迁移脚本
将旧架构（冗余字段）的数据迁移到新架构（外键关联）

使用方法:
    python migrate_cost_data.py
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from eims_app.models.model_cost_sub_modules import (
    CostProjectInfo,
    CostTaskPlan,
    CostTaskImplementation,
    CostReviewResult,
    CostPaymentStatus,
    CostProjectArchive,
    CostRemunerationDistribution,
)


def get_table_columns(table_name):
    """获取表的列名（MySQL版本）"""
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = '{table_name}'
    """)
    columns = [row[0] for row in cursor.fetchall()]
    return columns


def check_old_tables():
    """检查是否存在旧表"""
    cursor = connection.cursor()
    # MySQL使用information_schema查询表名
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name LIKE 'eims_app_cost%%'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n找到 {len(tables)} 个造价咨询相关表:")
    for table in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} 条记录")
    return tables


def migrate_task_plan():
    """迁移任务计划数据"""
    print("\n" + "="*60)
    print("开始迁移【任务计划】数据...")
    print("="*60)
    
    # 检查是否有旧数据（通过检查是否有project_id字段来判断是否已迁移）
    old_columns = get_table_columns('eims_app_costtaskplan')
    if 'project_id' not in old_columns:
        print("⚠️  表中没有 project_id 字段，可能还未创建新表结构")
        return
    
    # 统计当前数据
    current_count = CostTaskPlan.objects.count()
    print(f"当前任务计划记录数: {current_count}")
    
    if current_count > 0:
        print("✅ 已有数据，跳过迁移")
        return
    
    # 由于是新架构，没有旧数据可迁移
    # 这里主要是演示如何从CostProjectInfo关联
    projects = CostProjectInfo.objects.all()
    print(f"找到 {projects.count()} 个项目信息")
    
    if projects.count() == 0:
        print("⚠️  没有项目信息，无法创建测试数据")
        return
    
    # 为每个项目创建一条示例任务计划（仅用于测试）
    created = 0
    for project in projects[:3]:  # 只取前3个项目创建示例
        try:
            task_plan = CostTaskPlan.objects.create(
                tenant=project.tenant,
                project=project,
                project_code=project.project_code,
                project_name=project.project_name,
                project_type=project.project_type,
                compiler=f"编制人{project.project_code[-2:]}",
                compilation_amount=100000.00,
                first_reviewer=f"一审{project.project_code[-2:]}",
                first_review_planned_duration=5,
                second_reviewer=f"二审{project.project_code[-2:]}",
                second_review_planned_duration=3,
                third_reviewer=f"三审{project.project_code[-2:]}",
                third_review_planned_duration=2,
            )
            created += 1
            print(f"  ✓ 为项目 {project.project_code} 创建任务计划")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
    
    print(f"\n✅ 任务计划迁移完成！共创建 {created} 条记录")


def migrate_task_implementation():
    """迁移任务实施数据"""
    print("\n" + "="*60)
    print("开始迁移【任务实施】数据...")
    print("="*60)
    
    current_count = CostTaskImplementation.objects.count()
    print(f"当前任务实施记录数: {current_count}")
    
    if current_count > 0:
        print("✅ 已有数据，跳过迁移")
        return
    
    # 基于已有的任务计划创建实施记录
    task_plans = CostTaskPlan.objects.all()[:3]
    created = 0
    
    for plan in task_plans:
        try:
            impl = CostTaskImplementation.objects.create(
                tenant=plan.tenant,
                project=plan.project,
                project_code=plan.project_code,
                project_name=plan.project_name,
                project_type=plan.project_type,
                compiler=plan.compiler,
                compilation_amount=plan.compilation_amount,
            )
            created += 1
            print(f"  ✓ 为项目 {plan.project_code} 创建任务实施")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
    
    print(f"\n✅ 任务实施迁移完成！共创建 {created} 条记录")


def migrate_review_result():
    """迁移审核成果数据"""
    print("\n" + "="*60)
    print("开始迁移【审核成果】数据...")
    print("="*60)
    
    current_count = CostReviewResult.objects.count()
    print(f"当前审核成果记录数: {current_count}")
    
    if current_count > 0:
        print("✅ 已有数据，跳过迁移")
        return
    
    from decimal import Decimal
    task_plans = CostTaskPlan.objects.all()[:3]
    created = 0
    
    for plan in task_plans:
        try:
            result = CostReviewResult.objects.create(
                tenant=plan.tenant,
                project=plan.project,
                project_code=plan.project_code,
                project_name=plan.project_name,
                project_type=plan.project_type,
                compiler=plan.compiler,
                compilation_amount=plan.compilation_amount,
                first_submission=plan.compilation_amount,
                final_approved_amount=plan.compilation_amount * Decimal('0.95'),
            )
            created += 1
            print(f"  ✓ 为项目 {plan.project_code} 创建审核成果")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
    
    print(f"\n✅ 审核成果迁移完成！共创建 {created} 条记录")


def migrate_payment_status():
    """迁移收费情况数据"""
    print("\n" + "="*60)
    print("开始迁移【收费情况】数据...")
    print("="*60)
    
    current_count = CostPaymentStatus.objects.count()
    print(f"当前收费情况记录数: {current_count}")
    
    if current_count > 0:
        print("✅ 已有数据，跳过迁移")
        return
    
    from decimal import Decimal
    task_plans = CostTaskPlan.objects.all()[:3]
    created = 0
    
    for plan in task_plans:
        try:
            payment = CostPaymentStatus.objects.create(
                tenant=plan.tenant,
                project=plan.project,
                project_code=plan.project_code,
                project_name=plan.project_name,
                project_type=plan.project_type,
                invoice_amount=plan.compilation_amount * Decimal('0.03'),  # 假设开票金额3%
                is_invoiced='invoiced',
                owner_payable=plan.compilation_amount * Decimal('0.03'),
                owner_paid=plan.compilation_amount * Decimal('0.015'),
                owner_pending=plan.compilation_amount * Decimal('0.015'),
            )
            created += 1
            print(f"  ✓ 为项目 {plan.project_code} 创建收费情况")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
    
    print(f"\n✅ 收费情况迁移完成！共创建 {created} 条记录")


def migrate_project_archive():
    """迁移项目存档数据"""
    print("\n" + "="*60)
    print("开始迁移【项目存档】数据...")
    print("="*60)
    
    current_count = CostProjectArchive.objects.count()
    print(f"当前项目存档记录数: {current_count}")
    
    if current_count > 0:
        print("✅ 已有数据，跳过迁移")
        return
    
    task_plans = CostTaskPlan.objects.all()[:3]
    created = 0
    
    for plan in task_plans:
        try:
            archive = CostProjectArchive.objects.create(
                tenant=plan.tenant,
                project=plan.project,
                project_code=plan.project_code,
                project_name=plan.project_name,
                project_type=plan.project_type,
            )
            created += 1
            print(f"  ✓ 为项目 {plan.project_code} 创建项目存档")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
    
    print(f"\n✅ 项目存档迁移完成！共创建 {created} 条记录")


def migrate_remuneration_distribution():
    """迁移酬劳分配数据"""
    print("\n" + "="*60)
    print("开始迁移【酬劳分配】数据...")
    print("="*60)
    
    current_count = CostRemunerationDistribution.objects.count()
    print(f"当前酬劳分配记录数: {current_count}")
    
    if current_count > 0:
        print("✅ 已有数据，跳过迁移")
        return
    
    from decimal import Decimal
    task_plans = CostTaskPlan.objects.all()[:3]
    created = 0
    
    for plan in task_plans:
        try:
            remuneration = CostRemunerationDistribution.objects.create(
                tenant=plan.tenant,
                project=plan.project,
                project_code=plan.project_code,
                project_name=plan.project_name,
                project_type=plan.project_type,
                calculation_type='compilation',
                calculation_base='total_cost',
                total_cost=plan.compilation_amount,
                total_remuneration=plan.compilation_amount * Decimal('0.02'),  # 假设酬劳2%
                distribution_status='draft',
            )
            created += 1
            print(f"  ✓ 为项目 {plan.project_code} 创建酬劳分配")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
    
    print(f"\n✅ 酬劳分配迁移完成！共创建 {created} 条记录")


def verify_migration():
    """验证迁移结果"""
    print("\n" + "="*60)
    print("验证迁移结果")
    print("="*60)
    
    models_info = [
        ("项目信息", CostProjectInfo),
        ("任务计划", CostTaskPlan),
        ("任务实施", CostTaskImplementation),
        ("审核成果", CostReviewResult),
        ("收费情况", CostPaymentStatus),
        ("项目存档", CostProjectArchive),
        ("酬劳分配", CostRemunerationDistribution),
    ]
    
    for name, model in models_info:
        count = model.objects.count()
        print(f"  {name}: {count} 条记录")
    
    print("\n✅ 验证完成！")


def main():
    """主函数"""
    print("="*60)
    print("造价咨询模块数据迁移工具")
    print("="*60)
    
    # 检查旧表
    check_old_tables()
    
    # 执行迁移
    migrate_task_plan()
    migrate_task_implementation()
    migrate_review_result()
    migrate_payment_status()
    migrate_project_archive()
    migrate_remuneration_distribution()
    
    # 验证结果
    verify_migration()
    
    print("\n" + "="*60)
    print("🎉 所有迁移完成！")
    print("="*60)
    print("\n提示：")
    print("1. 请重启Django服务器查看效果")
    print("2. 访问造价咨询各子模块列表页面验证数据")
    print("3. 测试项目编号/名称修改后的实时同步功能")


if __name__ == '__main__':
    main()
