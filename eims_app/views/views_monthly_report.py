from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from datetime import date, timedelta
import django.db.models as models
from ..models import MonthlyReport
from ..models.model_user import ProjectReporter
from ..models.model_project_detail import ProjectDetail  # 改用 ProjectDetail
from ..forms.form_monthly_report import MonthlyReportForm, MonthlyReportFilterForm


@login_required
def monthly_report_list(request):
    """月度报告列表页面"""
    
    # 筛选表单
    filter_form = MonthlyReportFilterForm(request.GET or None)
    
    # 基础查询集
    reports = MonthlyReport.objects.select_related('project').all()
    
    # 非超级管理员只能查看自己负责的项目
    if not request.user.is_superuser:
        reports = reports.filter(
            Q(project__project_manager=request.user.username) |
            Q(reporter=request.user)
        )
    
    # 应用筛选
    if filter_form.is_valid():
        report_month = filter_form.cleaned_data.get('report_month')
        status = filter_form.cleaned_data.get('status')
        project = filter_form.cleaned_data.get('project')
        
        if report_month:
            # report_month 是字符串格式 "YYYY-MM"，直接使用
            reports = reports.filter(report_month=report_month)
        if status:
            reports = reports.filter(status=status)
        if project:
            reports = reports.filter(project=project)
    
    # 分页
    page = request.GET.get('page', 1)
    paginator = Paginator(reports, 15)
    page_obj = paginator.get_page(page)
    
    # 统计信息
    stats = {
        'total': reports.count(),
        'draft': reports.filter(status='draft').count(),
        'submitted': reports.filter(status='submitted').count(),
        'overdue': reports.filter(status='overdue').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'title': '月度报告',
    }
    
    return render(request, 'monthly_report/list.html', context)


@login_required
def monthly_report_create(request):
    """创建月度报告 - 仅对特定角色用户开放"""
    
    # 权限检查：仅允许管理员、超级管理员、主任、副主任、主管、总监
    from eims_app.models.model_department import DepartmentRole
    
    if not request.user.is_superuser:
        # 检查用户是否具有允许的角色类型
        allowed_roles = ['manager', 'deputy', 'supervisor']  # 部门经理、副职、主管
        has_allowed_role = DepartmentRole.objects.filter(
            user=request.user,
            role_type__in=allowed_roles
        ).exists()
        
        # 检查是否是主任、副主任、总监（在 role_name 中）
        has_director_role = DepartmentRole.objects.filter(
            user=request.user
        ).filter(
            models.Q(role_name__icontains='主任') | 
            models.Q(role_name__icontains='副主任') |
            models.Q(role_name__icontains='总监')
        ).exists()
        
        if not has_allowed_role and not has_director_role:
            messages.error(request, '❌ 您没有权限创建月度报告，只有管理员、超级管理员、主任、副主任、主管、总监可以创建')
            return redirect('eims_app:monthly_report_list')
    
    # 从 URL 参数获取项目和月份
    project_id = request.GET.get('project')
    month = request.GET.get('month')
    
    initial_project = None
    if project_id:
        try:
            initial_project = ProjectDetail.objects.get(pk=project_id)
        except Exception:  # 改为通用异常捕获
            pass
    
    if request.method == 'POST':
        form = MonthlyReportForm(
            request.POST,
            user=request.user,
            initial_project=initial_project
        )
        
        # 判断是保存还是提交
        action = request.GET.get('action', 'save')
        
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.project_code = report.project.project_code
            
            # 解析月份（更健壮的版本）
            try:
                report_month_str = str(report.report_month).strip()
                # 处理可能的日期对象
                if hasattr(report.report_month, 'strftime'):
                    report_month_str = report.report_month.strftime('%Y-%m')
                
                if '-' in report_month_str:
                    year, month = map(int, report_month_str.split('-'))
                    report.report_year = year
                    report.report_month = report_month_str  # 保存为 "YYYY-MM" 字符串
                    
                    # 计算应提交日期（当月 25 日）
                    from datetime import date
                    report.should_submit_date = date(year, month, 25)
            except (ValueError, AttributeError) as e:
                # 如果解析失败，使用当前年月作为默认值
                from django.utils import timezone
                now = timezone.now()
                report.report_year = now.year
                report.report_month = now.strftime('%Y-%m')  # 保存为字符串
                report.should_submit_date = date(now.year, now.month, 25)
            
            # 自动计算累计产值和回款（强制保留 2 位小数）
            from decimal import Decimal, ROUND_HALF_UP
            
            # 转换为 Decimal 进行精确计算
            last_output = Decimal(str(report.last_month_cumulative_output or 0))
            monthly_output = Decimal(str(report.monthly_output_value or 0))
            report.current_cumulative_output = (last_output + monthly_output).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            last_payment = Decimal(str(report.last_month_cumulative_payment or 0))
            monthly_payment = Decimal(str(report.monthly_payment or 0))
            report.current_cumulative_payment = (last_payment + monthly_payment).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # 设置实际提交时间为当前时间
            from django.utils import timezone
            report.actual_submit_date = timezone.now().date()
            
            # 根据操作类型设置状态
            if action == 'submit':
                report.status = 'submitted'
                report.submit_time = timezone.now()
                messages.success(request, '✓ 月度报告已提交！')
            else:
                report.status = 'draft'
                messages.success(request, '✓ 月度报告已保存为草稿！')
            
            report.save()
            
            # 如果是保存，重定向时带上 saved 参数
            if action == 'save':
                return redirect(f"{reverse('eims_app:monthly_report_list')}?saved=1")
            else:
                return redirect('eims_app:monthly_report_list')
    else:
        form = MonthlyReportForm(
            user=request.user,
            initial_project=initial_project
        )
    
    context = {
        'form': form,
        'title': '创建月度报告',
        'action': '创建',
        'subtitle': '填报项目月度动态信息',
    }
    
    return render(request, 'monthly_report/form.html', context)


@login_required
def monthly_report_edit(request, pk):
    """编辑月度报告"""
    
    report = get_object_or_404(MonthlyReport, pk=pk)
    
    # 权限检查
    if not request.user.is_superuser:
        if not (report.project.project_manager == request.user.username or
                report.reporter == request.user):
            messages.error(request, '您没有权限编辑此报告')
            return redirect('eims_app:monthly_report_list')
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.update_time = timezone.now()
            report.save()
            messages.success(request, '✓ 月度报告更新成功！')
            return redirect('eims_app:monthly_report_list')
    else:
        form = MonthlyReportForm(instance=report, user=request.user)
    
    context = {
        'form': form,
        'report': report,
        'title': '编辑月度报告',
        'action': '编辑',
    }
    
    return render(request, 'monthly_report/form.html', context)


@login_required
def monthly_report_submit(request, pk):
    """提交月度报告"""
    
    report = get_object_or_404(MonthlyReport, pk=pk)
    
    # 权限检查
    if not request.user.is_superuser:
        if not (report.project.project_manager == request.user.username):
            messages.error(request, '您没有权限提交此报告')
            return redirect('eims_app:monthly_report_list')
    
    if request.method == 'POST':
        report.status = 'submitted'
        report.submitter = request.user.username
        report.actual_submit_date = date.today()
        report.submit_time = timezone.now()
        report.save()
        
        messages.success(request, '✓ 月度报告已提交！')
        return redirect('eims_app:monthly_report_list')
    
    context = {
        'report': report,
        'title': '确认提交',
    }
    
    return render(request, 'monthly_report/confirm_submit.html', context)


@login_required
def monthly_report_detail(request, pk):
    """月度报告详情"""
    
    report = get_object_or_404(MonthlyReport.objects.select_related('project'), pk=pk)
    
    context = {
        'report': report,
        'title': '报告详情',
    }
    
    return render(request, 'monthly_report/detail.html', context)


@login_required
def monthly_report_dashboard(request):
    """月度填报仪表盘 - 显示待填报提醒"""
    
    today = date.today()
    current_month = timezone.now().strftime('%Y-%m')
    
    # 获取搜索参数
    search_query = request.GET.get('search', '').strip()
    
    # 获取所有项目（显示所有项目，不限制）
    projects = ProjectDetail.objects.all()
    
    # 如果有搜索关键词，进行模糊搜索
    if search_query:
        projects = projects.filter(
            Q(project_code__icontains=search_query) |
            Q(project_name__icontains=search_query)
        )
    
    # 需要填报的项目（本月还未填报的，且项目月报字段值为“需要”）
    needs_filling = []
    # 解析当前年份和月份
    current_year, current_month_num = map(int, current_month.split('-'))
        
    # 当前月份的字符串格式（用于查询）
    current_month_str = f"{current_year}-{current_month_num:02d}"  # 格式：YYYY-MM
        
    for project in projects:
        # 只处理“项目月报”字段值为 True 的项目（需要提交月报）
        if not project.monthly_report_required:
            continue
                
        # 修复：使用字符串格式的月份进行查询
        existing_report = MonthlyReport.objects.filter(
            project=project,
            report_year=current_year,
            report_month=current_month_str  # 使用字符串格式 "YYYY-MM"
        ).first()
            
        if not existing_report:
            # 计算应提交日期
            year, month = map(int, current_month.split('-'))
            due_date = date(year, month, 25)
            days_left = (due_date - today).days
                
            needs_filling.append({
                'project': project,
                'due_date': due_date,
                'days_left': days_left,
                'is_urgent': days_left <= 5,  # 少于 5 天为紧急
            })
    
    # 草稿状态的报告
    drafts = MonthlyReport.objects.filter(
        status='draft',
        reporter=request.user
    ).select_related('project')[:5]
    
    # 已逾期的报告
    overdue = MonthlyReport.objects.filter(
        status='overdue',
        reporter=request.user
    ).select_related('project')[:5]
    
    context = {
        'needs_filling': needs_filling,
        'drafts': drafts,
        'overdue': overdue,
        'projects': projects,  # 添加所有项目列表
        'search_query': search_query,  # 传递搜索关键词到模板
        'current_month': current_month,
        'today': today,
        'title': '月度填报提醒',
    }
    
    return render(request, 'monthly_report/dashboard.html', context)


@login_required
def get_pending_reports(request):
    """
    获取用户待填报的月度报告项目（API）
    返回：JSON 格式的项目列表
    """
    # 检查是否为每月最后 5 天
    today = date.today()
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    
    last_day_of_month = next_month - timedelta(days=1)
    is_last_five_days = (last_day_of_month.day - today.day) <= 4
    
    if not is_last_five_days:
        return JsonResponse({
            'success': True,
            'is_last_five_days': False,
            'pending_projects': [],
            'message': '当前不是每月最后 5 天'
        })
    
    # 获取当前年月
    report_year = today.year
    report_month = f"{today.year}-{today.month:02d}"
    
    # 查询该用户负责的所有项目（且需要填报月报）
    reporter_relations = ProjectReporter.objects.filter(
        user=request.user,
        is_active=True,
        project__monthly_report_required=True
    ).select_related('project')
    
    pending_projects = []
    
    for relation in reporter_relations:
        project = relation.project
        
        # 检查该项目是否已有当月的月度报告（排除草稿状态）
        existing_report = MonthlyReport.objects.filter(
            project=project,
            report_year=report_year,
            report_month=report_month,
            reporter=request.user
        ).exclude(status='draft').first()
        
        # 如果没有已提交的报告，则加入待填报列表
        if not existing_report:
            pending_projects.append({
                'project_id': project.id,
                'project_code': project.project_code,
                'project_name': project.project_name,
                'detail_url': reverse('eims_app:project_ledger_detail', kwargs={'pk': project.id})
            })
    
    return JsonResponse({
        'success': True,
        'is_last_five_days': True,
        'pending_projects': pending_projects,
        'count': len(pending_projects),
        'message': f'您有 {len(pending_projects)} 个项目需要填报月度报告'
    })


@login_required
def clear_reminder(request):
    """
    清除提醒标记（当用户完成填报后调用）
    """
    if 'monthly_report_reminder' in request.session:
        del request.session['monthly_report_reminder']
    
    return JsonResponse({'success': True})
    return render(request, 'monthly_report/dashboard.html', context)
