"""
月度报告提醒中间件
在每月最后 5 天，用户登录后弹出提醒窗口
"""
from datetime import date, timedelta
from django.shortcuts import redirect
from eims_app.models.model_user import ProjectReporter, MonthlyReport


def is_last_five_days_of_month():
    """判断当前是否为每月最后 5 天"""
    today = date.today()
    # 获取当月最后一天
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    
    last_day_of_month = next_month - timedelta(days=1)
    # 计算最后 5 天的起始日期
    last_five_days_start = last_day_of_month - timedelta(days=4)
    
    return last_day_of_month.day - today.day <= 4


def get_pending_reports_for_user(user):
    """
    获取用户需要填报但还未填报的月度报告项目
    返回：[(project, has_submitted), ...]
    """
    if not user.is_authenticated:
        return []
    
    # 获取当前年月
    today = date.today()
    report_year = today.year
    report_month = f"{today.year}-{today.month:02d}"
    
    # 查询该用户负责的所有项目（且需要填报月报）
    reporter_relations = ProjectReporter.objects.filter(
        user=user,
        is_active=True,
        project__monthly_report_required=True
    ).select_related('project')
    
    pending_projects = []
    
    for relation in reporter_relations:
        project = relation.project
        
        # 检查该项目是否已有当月的月度报告
        existing_report = MonthlyReport.objects.filter(
            project=project,
            report_year=report_year,
            report_month=report_month,
            reporter=user
        ).exclude(status='draft').first()
        
        # 如果没有已提交的报告，则加入待填报列表
        if not existing_report:
            pending_projects.append({
                'project_id': project.id,
                'project_code': project.project_code,
                'project_name': project.project_name,
            })
    
    return pending_projects


def monthly_report_reminder_middleware(get_response):
    """
    月度报告提醒中间件
    在每月最后 5 天检查用户是否有待填报的月度报告
    """
    def middleware(request):
        # 只对已登录用户生效
        if request.user.is_authenticated:
            # 检查是否为每月最后 5 天
            if is_last_five_days_of_month():
                # 获取用户待填报的项目
                pending_projects = get_pending_reports_for_user(request.user)
                
                # 如果有待填报的项目，添加到 request 中
                if pending_projects:
                    request.session['monthly_report_reminder'] = {
                        'pending_projects': pending_projects,
                        'is_last_five_days': True,
                    }
                else:
                    # 清除提醒
                    if 'monthly_report_reminder' in request.session:
                        del request.session['monthly_report_reminder']
            else:
                # 不是最后 5 天，清除提醒
                if 'monthly_report_reminder' in request.session:
                    del request.session['monthly_report_reminder']
        
        response = get_response(request)
        return response
    
    return middleware
