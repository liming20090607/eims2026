#!/usr/bin/env python
"""
造价咨询数据迁移脚本 - 从7表架构迁移到统一表架构

使用方法:
    python migrate_cost_to_unified.py
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
    CostRemunerationItem as OldRemunerationItem,
)
from eims_app.models.model_cost_unified import (
    CostProjectUnified,
    CostUnifiedRemunerationItem,
)


def migrate_data():
    """执行数据迁移"""
    print("="*70)
    print("造价咨询数据迁移 - 7表架构 -> 统一表架构")
    print("="*70)
    
    # 获取所有项目
    projects = CostProjectInfo.objects.all()
    print(f"\n找到 {projects.count()} 个项目需要迁移\n")
    
    migrated_count = 0
    error_count = 0
    skipped_count = 0
    
    for idx, project in enumerate(projects, 1):
        try:
            # 检查是否已迁移
            if CostProjectUnified.objects.filter(project_code=project.project_code).exists():
                print(f"[{idx}/{projects.count()}] 跳过已迁移项目: {project.project_code}")
                skipped_count += 1
                continue
            
            print(f"[{idx}/{projects.count()}] 迁移项目: {project.project_code} - {project.project_name}")
            
            # 创建统一记录 - 基础字段
            unified = CostProjectUnified(
                tenant=project.tenant,
                created_at=project.created_at,
                update_time=project.update_time,
                operator=project.operator,
                approval_status=project.approval_status,
                current_approver=project.current_approver,
                approval_department=project.approval_department,
                approval_level=project.approval_level,
                submit_time=project.submit_time,
                approval_time=project.approval_time,
                approval_remark=project.approval_remark,
                
                # 模块1: 项目信息
                project_code=project.project_code,
                project_name=project.project_name,
                project_type=project.project_type,
                compilation_category=project.compilation_category,
                review_category=project.review_category,
                project_status=project.project_status,
                client_unit=project.client_unit,
                entrusting_unit=project.entrusting_unit,
                contact_person=project.contact_person,
                contact_phone=project.contact_phone,
                submission_time=project.submission_time,
                start_time=project.start_time,
                planned_duration=project.planned_duration,
                planned_completion_time=project.planned_completion_time,
                compilation_amount=project.compilation_amount,
                submission_amount=project.submission_amount,
                approved_amount=project.approved_amount,
                reduced_amount=project.reduced_amount,
                report_time=project.report_time,
                result_confirm=project.result_confirm,
                total_fee=project.total_fee,
                received_fee=project.received_fee,
                pending_fee=project.pending_fee,
                fee_settlement=project.fee_settlement,
            )
            
            # 模块2: 任务计划
            task_plan = CostTaskPlan.objects.filter(project=project).first()
            if task_plan:
                unified.plan_compiler = task_plan.compiler
                unified.plan_compiler_personnel = task_plan.compiler_personnel
                unified.plan_compilation_amount = task_plan.compilation_amount
                unified.plan_first_reviewer = task_plan.first_reviewer
                unified.plan_first_reviewer_personnel = task_plan.first_reviewer_personnel
                unified.plan_first_reviewer_department = task_plan.first_reviewer_department
                unified.plan_first_review_start_time = task_plan.first_review_start_time
                unified.plan_first_review_planned_duration = task_plan.first_review_planned_duration
                unified.plan_first_review_planned_completion = task_plan.first_review_planned_completion
                unified.plan_second_reviewer = task_plan.second_reviewer
                unified.plan_second_reviewer_personnel = task_plan.second_reviewer_personnel
                unified.plan_second_reviewer_department = task_plan.second_reviewer_department
                unified.plan_second_review_start_time = task_plan.second_review_start_time
                unified.plan_second_review_planned_duration = task_plan.second_review_planned_duration
                unified.plan_second_review_planned_completion = task_plan.second_review_planned_completion
                unified.plan_third_reviewer = task_plan.third_reviewer
                unified.plan_third_reviewer_personnel = task_plan.third_reviewer_personnel
                unified.plan_third_reviewer_department = task_plan.third_reviewer_department
                unified.plan_third_review_start_time = task_plan.third_review_start_time
                unified.plan_third_review_planned_duration = task_plan.third_review_planned_duration
                unified.plan_third_review_planned_completion = task_plan.third_review_planned_completion
                print("   [OK] 任务计划数据")
            
            # 模块3: 任务实施
            task_impl = CostTaskImplementation.objects.filter(project=project).first()
            if task_impl:
                unified.impl_compiler = task_impl.compiler
                unified.impl_compiler_personnel = task_impl.compiler_personnel
                unified.impl_compilation_amount = task_impl.compilation_amount
                # 一审实际
                unified.impl_first_reviewer_personnel = task_impl.first_reviewer_personnel
                unified.impl_first_review_planned_duration = task_impl.first_review_planned_duration
                unified.impl_first_review_planned_completion = task_impl.first_review_planned_completion
                unified.impl_first_review_actual_completion = task_impl.first_review_actual_completion
                unified.impl_first_review_actual_duration = task_impl.first_review_actual_duration
                unified.impl_first_review_progress_result = task_impl.first_review_progress_result
                print("   [OK] 任务实施数据")
            
            # 模块4: 审核成果
            review = CostReviewResult.objects.filter(project=project).first()
            if review:
                unified.review_compiler = review.compiler
                unified.review_compilation_amount = review.compilation_amount
                unified.review_first_submission = review.first_submission
                unified.review_first_result = review.first_result
                unified.review_first_reduction = review.first_reduction
                unified.review_first_reduction_rate = review.first_reduction_rate
                unified.review_first_review_evaluation = review.first_review_evaluation
                unified.review_second_submission = review.second_submission
                unified.review_second_result = review.second_result
                unified.review_second_reduction = review.second_reduction
                unified.review_second_reduction_rate = review.second_reduction_rate
                unified.review_second_reviewer = review.second_reviewer
                unified.review_second_evaluation = review.second_evaluation
                unified.review_third_submission = review.third_submission
                unified.review_third_result = review.third_result
                unified.review_third_reduction = review.third_reduction
                unified.review_third_reduction_rate = review.third_reduction_rate
                unified.review_third_reviewer = review.third_reviewer
                unified.review_third_evaluation = review.third_evaluation
                unified.review_final_approved_amount = review.final_approved_amount
                print("   [OK] 审核成果数据")
            
            # 模块5: 收费情况
            payment = CostPaymentStatus.objects.filter(project=project).first()
            if payment:
                unified.payment_invoice_amount = payment.invoice_amount
                unified.payment_is_invoiced = payment.is_invoiced
                unified.payment_owner_payable = payment.owner_payable
                unified.payment_owner_paid = payment.owner_paid
                unified.payment_owner_pending = payment.owner_pending
                unified.payment_contractor_payable = payment.contractor_payable
                unified.payment_contractor_paid = payment.contractor_paid
                unified.payment_contractor_pending = payment.contractor_pending
                unified.payment_is_settled = payment.is_settled
                print("   [OK] 收费情况数据")
            
            # 模块6: 项目存档
            archive = CostProjectArchive.objects.filter(project=project).first()
            if archive:
                unified.archive_status = archive.archive_status
                unified.archive_electronic = archive.electronic_archive
                unified.archive_paper = archive.paper_archive
                unified.archive_complete = archive.archive_complete
                unified.archive_location = archive.archive_location
                unified.archive_date = archive.archive_date
                unified.archive_remark = archive.archive_remark
                print("   [OK] 项目存档数据")
            
            # 模块7: 酬劳分配
            remuneration = CostRemunerationDistribution.objects.filter(project=project).first()
            if remuneration:
                unified.remuneration_calculation_type = remuneration.calculation_type
                unified.remuneration_calculation_base = remuneration.calculation_base
                unified.remuneration_total_cost = remuneration.total_cost
                unified.remuneration_reduced_amount = remuneration.reduced_amount
                unified.remuneration_total_remuneration = remuneration.total_remuneration
                unified.remuneration_calculation_formula = remuneration.calculation_formula
                unified.remuneration_distribution_status = remuneration.distribution_status
                unified.remuneration_compiler_ratio = remuneration.compiler_ratio
                unified.remuneration_first_reviewer_ratio = remuneration.first_reviewer_ratio
                unified.remuneration_second_reviewer_ratio = remuneration.second_reviewer_ratio
                unified.remuneration_third_reviewer_ratio = remuneration.third_reviewer_ratio
                print("   [OK] 酬劳分配数据")
                
                # 迁移酬劳明细
                old_items = OldRemunerationItem.objects.filter(distribution=remuneration)
                if old_items.exists():
                    for old_item in old_items:
                        CostUnifiedRemunerationItem.objects.create(
                            project=unified,
                            person_name=old_item.person_name,
                            person_id_card=old_item.person_id_card,
                            role=old_item.role,
                            ratio=old_item.ratio,
                            amount=old_item.amount,
                        )
                    print(f"   [OK] 酬劳明细 ({old_items.count()}条)")
            
            # 保存统一记录
            unified.save()
            migrated_count += 1
            print(f"   [SUCCESS] 迁移成功\n")
            
        except Exception as e:
            error_count += 1
            print(f"   [ERROR] 迁移失败: {e}\n")
            import traceback
            traceback.print_exc()
    
    # 打印总结
    print("\n" + "="*70)
    print("迁移完成!")
    print("="*70)
    print(f"  成功迁移: {migrated_count} 个项目")
    print(f"  跳过(已存在): {skipped_count} 个项目")
    print(f"  迁移失败: {error_count} 个项目")
    print(f"  总计处理: {projects.count()} 个项目")
    print("="*70)
    
    # 验证迁移结果
    print("\n验证迁移结果...")
    unified_count = CostProjectUnified.objects.count()
    print(f"  统一表记录数: {unified_count}")
    
    if unified_count > 0:
        sample = CostProjectUnified.objects.first()
        print(f"  示例项目: {sample.project_code} - {sample.project_name}")
        print("\n迁移验证通过！")
    else:
        print("\n警告: 统一表中没有数据！")


if __name__ == '__main__':
    migrate_data()
