from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from ..models import MonthlyReport, ApprovalFlow, ApprovalRecord, ProjectRole, Role


@login_required
def approval_flow_list(request):
    """审批流程列表"""
    
    # 获取用户有权限查看的流程
    if request.user.is_superuser:
        flows = ApprovalFlow.objects.all()
    else:
        # 用户参与的项目
        project_roles = ProjectRole.objects.filter(user=request.user, is_active=True)
        project_ids = [pr.project_id for pr in project_roles]
        
        flows = ApprovalFlow.objects.filter(
            Q(report__project_id__in=project_ids) |
            Q(initiator=request.user) |
            Q(director=request.user) |
            Q(approver=request.user)
        )
    
    # 筛选
    status = request.GET.get('status', '')
    if status:
        flows = flows.filter(status=status)
    
    # 分页
    paginator = Paginator(flows.order_by('-initiate_time'), 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'status_choices': ApprovalFlow.FLOW_STATUS_CHOICES,
        'title': '审批流程管理',
    }
    
    return render(request, 'workflow/flow_list.html', context)


@login_required
def approval_flow_detail(request, pk):
    """审批流程详情"""
    
    flow = get_object_or_404(ApprovalFlow, pk=pk)
    
    # 权限检查
    if not request.user.is_superuser:
        has_permission = (
            flow.initiator == request.user or
            flow.director == request.user or
            flow.approver == request.user or
            ProjectRole.objects.filter(
                user=request.user,
                project=flow.report.project,
                is_active=True
            ).exists()
        )
        if not has_permission:
            messages.error(request, '您没有权限查看此流程')
            return redirect('approval_flow_list')
    
    # 获取审批记录
    records = ApprovalRecord.objects.filter(flow=flow).order_by('-action_time')
    
    context = {
        'flow': flow,
        'records': records,
        'title': '审批流程详情',
    }
    
    return render(request, 'workflow/flow_detail.html', context)


@login_required
def submit_for_review(request, report_id):
    """提交报告给总监审核"""
    
    report = get_object_or_404(MonthlyReport, pk=report_id)
    
    # 权限检查 - 只有项目人员可以提交
    if not request.user.is_superuser:
        has_permission = ProjectRole.objects.filter(
            user=request.user,
            project=report.project,
            is_active=True
        ).exists()
        if not has_permission:
            messages.error(request, '您没有权限提交此报告')
            return redirect('monthly_report_list')
    
    if request.method == 'POST':
        # 更新报告状态
        report.status = 'pending_review'
        report.save()
        
        # 创建或更新审批流程
        flow, created = ApprovalFlow.objects.get_or_create(
            report=report,
            defaults={
                'initiator': request.user,
                'status': 'pending_review',
                'current_step': 1
            }
        )
        
        if not created:
            flow.status = 'pending_review'
            flow.current_step = 1
            flow.save()
        
        # 记录操作
        ApprovalRecord.objects.create(
            flow=flow,
            action='submit',
            operator=request.user,
            opinion='提交审核'
        )
        
        messages.success(request, '✓ 报告已提交，等待总监审核')
        return redirect('approval_flow_detail', pk=flow.pk)
    
    context = {
        'report': report,
        'title': '确认提交',
    }
    
    return render(request, 'workflow/confirm_submit.html', context)


@login_required
def director_review(request, flow_id):
    """总监审核"""
    
    flow = get_object_or_404(ApprovalFlow, pk=flow_id)
    
    # 权限检查 - 只有项目总监可以审核
    if not request.user.is_superuser:
        if flow.director != request.user:
            # 检查是否是项目总监
            is_director = ProjectRole.objects.filter(
                user=request.user,
                project=flow.report.project,
                role__name='project_director',
                is_active=True
            ).exists()
            if not is_director:
                messages.error(request, '您没有权限审核此报告')
                return redirect('approval_flow_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'pass' or 'reject'
        opinion = request.POST.get('opinion', '')
        
        if action == 'pass':
            flow.director_passed = True
            flow.status = 'pending_approval'
            flow.current_step = 2
            messages.success(request, '✓ 审核通过，已提交管理员审批')
            
            # 更新报告状态
            flow.report.status = 'pending_approval'
            flow.report.save()
            
            # 记录操作
            ApprovalRecord.objects.create(
                flow=flow,
                action='review_pass',
                operator=request.user,
                opinion=opinion or '审核通过'
            )
            
        elif action == 'reject':
            flow.director_passed = False
            flow.status = 'rejected'
            
            # 更新报告状态
            flow.report.status = 'rejected'
            flow.report.reject_reason = opinion
            flow.report.save()
            
            # 记录操作
            ApprovalRecord.objects.create(
                flow=flow,
                action='review_reject',
                operator=request.user,
                opinion=opinion or '审核不通过'
            )
            
            messages.warning(request, '✗ 已退回报告')
        
        flow.director_opinion = opinion
        flow.director_review_time = timezone.now()
        flow.director = request.user
        flow.save()
        
        return redirect('approval_flow_detail', pk=flow.pk)
    
    context = {
        'flow': flow,
        'title': '总监审核',
    }
    
    return render(request, 'workflow/director_review.html', context)


@login_required
def admin_approval(request, flow_id):
    """管理员审批"""
    
    flow = get_object_or_404(ApprovalFlow, pk=flow_id)
    
    # 权限检查 - 只有管理员可以审批
    if not request.user.is_superuser:
        messages.error(request, '您没有权限审批此报告')
        return redirect('approval_flow_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'pass' or 'reject'
        opinion = request.POST.get('opinion', '')
        
        if action == 'pass':
            flow.approval_passed = True
            flow.status = 'approved'
            
            # 更新报告状态
            flow.report.status = 'approved'
            flow.report.save()
            
            # 记录操作
            ApprovalRecord.objects.create(
                flow=flow,
                action='approve_pass',
                operator=request.user,
                opinion=opinion or '审批通过'
            )
            
            messages.success(request, '✓ 审批通过！')
            
        elif action == 'reject':
            flow.approval_passed = False
            flow.status = 'rejected'
            
            # 更新报告状态
            flow.report.status = 'rejected'
            flow.report.reject_reason = opinion
            flow.report.save()
            
            # 记录操作
            ApprovalRecord.objects.create(
                flow=flow,
                action='approve_reject',
                operator=request.user,
                opinion=opinion or '审批不通过'
            )
            
            messages.warning(request, '✗ 已退回报告')
        
        flow.approval_opinion = opinion
        flow.approval_time = timezone.now()
        flow.approver = request.user
        flow.save()
        
        return redirect('approval_flow_detail', pk=flow.pk)
    
    context = {
        'flow': flow,
        'title': '管理员审批',
    }
    
    return render(request, 'workflow/admin_approval.html', context)


@login_required
def my_pending_reviews(request):
    """我待审核的报告"""
    
    # 查找需要当前用户审核的流程
    pending_flows = ApprovalFlow.objects.filter(
        director=request.user,
        status='pending_review'
    ) | ApprovalFlow.objects.filter(
        approver=request.user,
        status='pending_approval'
    )
    
    context = {
        'pending_flows': pending_flows,
        'title': '我待审核的',
    }
    
    return render(request, 'workflow/my_pending.html', context)
