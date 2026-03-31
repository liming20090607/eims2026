from django.views.generic import TemplateView
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.utils import timezone
from datetime import date
from eims_app.models.model_project_detail import ProjectDetail  # 改用 ProjectDetail
from eims_app.models.model_contract import Contract
from eims_app.models import MonthlyReport

@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取项目统计数据
        context['total_projects'] = ProjectDetail.objects.count()
        context['active_projects'] = ProjectDetail.objects.filter(project_status='under_construction').count()
        context['delayed_projects'] = ProjectDetail.objects.filter(is_delayed=True).count() if hasattr(ProjectDetail, 'is_delayed') else 0
        context['completed_projects'] = ProjectDetail.objects.filter(project_status='completed').count()
        
        # 获取合同统计数据 - 修正字段名称
        context['total_contracts'] = Contract.objects.count()
        context['active_contracts'] = Contract.objects.filter(status='active').count()
        context['expired_contracts'] = Contract.objects.filter(status='expired').count()
        context['recent_contracts'] = Contract.objects.order_by('-signing_time')[:5]
                
        # 获取最近的项目
        context['recent_projects'] = ProjectDetail.objects.order_by('-created_at')[:5]
        
        # 获取最近的合同 - 修正字段名称
        context['recent_contracts'] = Contract.objects.order_by('-signing_time')[:5]
        
        # 获取月报提醒数据
        user = self.request.user
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        current_month_str = f"{current_year}-{current_month:02d}"
        
        # 获取用户参与的项目（通过 Personnel 分配）
        from eims_app.models import Personnel
        if user.is_superuser:
            # 超级管理员查看所有项目
            user_projects = ProjectDetail.objects.all()
        else:
            # 通过 Personnel 表查找用户参与的所有项目
            # 假设 user.username 与 Personnel.name 匹配
            personnel_records = Personnel.objects.filter(
                name=user.username
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
                project_manager=user.username
            ).values_list('id', flat=True)
            project_ids.update(manager_projects)
            
            # 获取用户参与的所有项目
            user_projects = ProjectDetail.objects.filter(
                id__in=list(project_ids)
            ) if project_ids else ProjectDetail.objects.none()
        
        # 获取已填报的月报
        existing_reports = MonthlyReport.objects.filter(
            project__in=user_projects,
            report_year=current_year,
            report_month=current_month_str
        )
        
        # 未填报的项目
        unreported_projects = user_projects.exclude(
            id__in=existing_reports.values_list('project_id', flat=True)
        )
        
        # 检查是否有已逾期的月报
        overdue_reports = MonthlyReport.objects.filter(
            project__in=user_projects,
            status='overdue'
        ).select_related('project')[:5]
        
        context['unreported_count'] = unreported_projects.count()
        context['unreported_projects'] = list(unreported_projects[:10])  # 最多 10 个
        context['overdue_reports'] = overdue_reports
        context['has_report_reminder'] = unreported_projects.count() > 0 or overdue_reports.count() > 0
        
        return context


def system_navigation(request):
    """系统功能模块导航页面"""
    context = {
        'home_url': '/',
        'eims_index_url': '/',
    }
    return render(request, 'system/navigation.html', context)