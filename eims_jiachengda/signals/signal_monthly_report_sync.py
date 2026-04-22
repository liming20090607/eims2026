"""
月度报告数据同步信号 - 当月度报告提交时，自动同步数据到项目管理模块
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ..models import MonthlyReport, ProjectDynamic, Personnel
from decimal import Decimal, ROUND_HALF_UP


@receiver(post_save, sender=MonthlyReport)
def sync_monthly_report_to_project_modules(sender, instance, created, **kwargs):
    """
    当月度报告提交时，自动同步数据到项目管理模块的三个子窗体
    
    触发条件：
    1. 月度报告状态变为 'submitted' (已提交)
    2. 或者新建报告时直接提交
    
    同步内容：
    1. 项目动态 (ProjectDynamic)
    2. 产值回款 (OutputPayment)
    3. 项目人员 (Personnel) - 仅更新人员总数和变动信息
    """
    
    # 只在报告提交时同步
    if instance.status != 'submitted':
        return
    
    # 检查是否已经同步过（避免重复同步）
    if hasattr(instance, '_synced_to_project'):
        return
    
    try:
        # 获取项目信息
        project = instance.project
        
        # 1. 同步到项目动态
        sync_to_project_dynamic(instance, project)
        
        # 2. 同步到产值回款
        sync_to_output_payment(instance, project)
        
        # 3. 同步到项目人员（更新人员变动信息）
        sync_to_personnel(instance, project)
        
        # 标记已同步
        instance._synced_to_project = True
        
    except Exception as e:
        # 记录错误但不影响主流程
        print(f"月度报告数据同步失败：{str(e)}")


def sync_to_project_dynamic(report, project):
    """
    同步月度报告数据到项目动态表
    
    同步字段：
    - project_progress: 项目进度说明
    - project_status: 当前状态
    - personnel_change: 本月人员变动
    """
    
    try:
        # 检查是否已存在相同月份的动态记录
        existing_dynamic = ProjectDynamic.objects.filter(
            project=project,
            create_time__year=report.report_year,
            create_time__month=int(report.report_month.split('-')[1])
        ).first()
        
        if existing_dynamic:
            # 更新现有记录
            existing_dynamic.project_progress = report.project_progress or ''
            existing_dynamic.project_status = report.current_status or ''
            existing_dynamic.personnel_change = report.personnel_changes or ''
            existing_dynamic.operator = report.reporter.username
            existing_dynamic.save()
        else:
            # 创建新记录
            ProjectDynamic.objects.create(
                project=project,
                project_code=project.project_code if project else '',
                project_progress=report.project_progress or '',
                project_status=report.current_status or '',
                personnel_change=report.personnel_changes or '',
                operator=report.reporter.username,
                remark=f'自动同步自月度报告 {report.report_year}-{report.report_month}'
            )
    except Exception as e:
        print(f"同步项目动态失败：{str(e)}")


def sync_to_output_payment(report, project):
    """
    同步月度报告数据到产值回款表
    
    同步字段：
    - month: 月份
    - monthly_output: 本月完成产值
    - cumulative_output: 本月累计产值
    - actual_payment: 本月实际回款
    - cumulative_received: 本月累计回款
    - next_month_plan: 下月请款金额
    - next_month_request: 下月计划详情
    - payment_measures: 请款措施
    - need_assistance: 需要协助
    """
    
    try:
        # 检查是否已存在相同月份的产值回款记录
        existing_output = OutputPayment.objects.filter(
            project=project,
            month=report.report_month
        ).first()
        
        if existing_output:
            # 更新现有记录
            existing_output.monthly_output = report.monthly_output_value or 0
            existing_output.cumulative_output = report.current_cumulative_output or 0
            existing_output.actual_payment = report.monthly_payment or 0
            existing_output.cumulative_received = report.current_cumulative_payment or 0
            existing_output.next_month_plan = report.next_month_plan_amount or 0
            existing_output.next_month_request = report.next_month_plan_detail or ''
            existing_output.payment_measures = report.payment_progress or ''
            existing_output.need_assistance = report.next_month_assistance or ''
            existing_output.operator = report.reporter.username
            existing_output.save()
        else:
            # 创建新记录
            OutputPayment.objects.create(
                project=project,
                project_code=project.project_code if project else '',
                month=report.report_month,
                monthly_output=report.monthly_output_value or 0,
                cumulative_output=report.current_cumulative_output or 0,
                actual_payment=report.monthly_payment or 0,
                cumulative_received=report.current_cumulative_payment or 0,
                next_month_plan=report.next_month_plan_amount or 0,
                next_month_request=report.next_month_plan_detail or '',
                payment_measures=report.payment_progress or '',
                need_assistance=report.next_month_assistance or '',
                operator=report.reporter.username,
                remark=f'自动同步自月度报告 {report.report_year}-{report.report_month}'
            )
    except Exception as e:
        print(f"同步产值回款失败：{str(e)}")


def sync_to_personnel(report, project):
    """
    同步月度报告数据到项目人员表（仅更新人员变动信息）
    
    同步字段：
    - personnel_change: 本月人员变动
    - total_personnel: 当前总人数
    
    注意：这里不直接创建人员记录，而是更新人员变动的备注信息
    """
    
    try:
        # 检查是否有人员变动或总人数信息
        if not report.personnel_changes and not report.total_personnel:
            return
        
        # 查找该项目的主要人员记录（用于记录人员变动信息）
        main_personnel = Personnel.objects.filter(
            project=project,
            is_deleted=False
        ).order_by('-create_time').first()
        
        if main_personnel:
            # 在主要人员记录的备注中记录人员变动信息
            change_info = f"[{report.report_month}] 人员变动：{report.personnel_changes or '无'}，总人数：{report.total_personnel or 0}人\n"
            if main_personnel.remark:
                main_personnel.remark = change_info + main_personnel.remark
            else:
                main_personnel.remark = change_info
            main_personnel.save()
        else:
            # 如果没有人员记录，创建一个汇总记录
            Personnel.objects.create(
                project=project,
                project_code=project.project_code if project else '',
                name=f'{project.project_name} - 人员汇总',
                personnel_code=f'PERSONNEL_{project.project_code}' if project else '',
                position='项目人员汇总',
                remark=f'[{report.report_month}] 人员变动：{report.personnel_changes or "无"}，总人数：{report.total_personnel or 0}人',
                operator=report.reporter.username
            )
    except Exception as e:
        print(f"同步项目人员失败：{str(e)}")
