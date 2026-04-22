"""
月报提醒相关视图
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from ..models import MonthlyReport
from ..models.model_project_detail import ProjectDetail


@login_required
def get_monthly_report_reminders(request):
    """获取当前用户的月报填报提醒（AJAX 接口）
    
    返回用户负责的项目中需要填报但尚未填报的月报信息
    """
    try:
        # 获取当前年月
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        current_month_str = f"{current_year}-{current_month:02d}"
        
        # 获取用户参与的项目（通过 Personnel 分配）
        from eims_app.models import Personnel
        if request.user.is_superuser:
            # 超级管理员查看所有项目（按租户过滤）
            project_filter = {'is_deleted': False}
            if hasattr(request, 'tenant') and request.tenant:
                project_filter['tenant_id'] = request.tenant.id
            user_projects = ProjectDetail.objects.filter(**project_filter)
        else:
            # 通过 Personnel 表查找用户参与的所有项目
            # 假设 request.user.username 与 Personnel.name 匹配
            personnel_records = Personnel.objects.filter(
                name=request.user.username,
                is_deleted=False
            )
            
            # 收集所有项目 ID
            project_ids = set()
            for p in personnel_records:
                if p.project_id:
                    project_ids.add(p.project_id)
                if hasattr(p, 'project2_id') and p.project2_id:
                    project_ids.add(p.project2_id)
                if hasattr(p, 'project3_id') and p.project3_id:
                    project_ids.add(p.project3_id)
                if hasattr(p, 'project4_id') and p.project4_id:
                    project_ids.add(p.project4_id)
                if hasattr(p, 'project5_id') and p.project5_id:
                    project_ids.add(p.project5_id)
            
            # 另外也检查 project_manager 字段（兼容旧逻辑）
            manager_projects = ProjectDetail.objects.filter(
                project_manager=request.user.username
            ).values_list('id', flat=True)
            project_ids.update(manager_projects)
            
            # 获取用户参与的所有项目
            user_projects = ProjectDetail.objects.filter(
                id__in=list(project_ids),
                is_deleted=False
            ) if project_ids else ProjectDetail.objects.none()
        
        # 获取这些项目在当前月份的月报记录
        existing_reports = MonthlyReport.objects.filter(
            project__in=user_projects,
            report_year=current_year,
            report_month=current_month_str
        )
        
        # 已填报的项目 ID
        reported_project_ids = existing_reports.values_list('project_id', flat=True)
        
        # 未填报的项目
        unreported_projects = user_projects.exclude(
            id__in=reported_project_ids
        )
        
        # 构建提醒数据
        reminders = []
        for project in unreported_projects[:10]:  # 最多显示 10 条
            # 检查该项目是否有历史月报记录
            has_history = MonthlyReport.objects.filter(
                project=project
            ).exists()
            
            # 只提醒有历史报告的项目（避免新项目被频繁提醒）
            if has_history or True:  # 暂时所有项目都提醒
                reminders.append({
                    'project_id': project.id,
                    'project_code': project.project_code,
                    'project_name': project.project_name,
                    'report_month': current_month_str,
                    'due_date': f"{current_year}-{current_month:02d}-25",
                    'days_remaining': (date(current_year, current_month, 25) - date.today()).days
                })
        
        # 检查是否有已逾期的月报
        overdue_reports = MonthlyReport.objects.filter(
            project__in=user_projects,
            status='overdue'
        ).select_related('project')[:5]  # 最多 5 条
        
        overdue_list = []
        for report in overdue_reports:
            overdue_list.append({
                'report_id': report.id,
                'project_code': report.project_code,
                'project_name': report.project.project_name,
                'report_month': report.report_month,
                'days_overdue': (date.today() - report.should_submit_date).days if report.should_submit_date else 0
            })
        
        return JsonResponse({
            'success': True,
            'current_month': current_month_str,
            'unreported_count': unreported_projects.count(),
            'reminders': reminders,
            'overdue_count': overdue_reports.count(),
            'overdue_reports': overdue_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
