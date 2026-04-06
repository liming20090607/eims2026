from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from eims_app.models.model_contract_approval import ContractApproval


@login_required
def my_pending_approvals(request):
    """我的待审批合同列表"""
    
    # 获取当前用户待审批的合同
    pending_approvals = ContractApproval.objects.filter(
        current_approver=request.user,
        status__in=['pending', 'reviewing']
    ).select_related('applicant', 'department').order_by('-created_at')
    
    # 统计数量
    total_count = pending_approvals.count()
    
    # 按状态分组统计
    pending_count = pending_approvals.filter(status='pending').count()
    reviewing_count = pending_approvals.filter(status='reviewing').count()
    
    context = {
        'pending_approvals': pending_approvals,
        'total_count': total_count,
        'pending_count': pending_count,
        'reviewing_count': reviewing_count,
        'title': '我的待审批',
    }
    
    return render(request, 'contract_management/my_pending_approvals.html', context)


@login_required
def my_initiated_approvals(request):
    """我发起的审批列表"""
    
    # 获取当前用户发起的审批
    initiated_approvals = ContractApproval.objects.filter(
        applicant=request.user
    ).select_related('current_approver', 'department').order_by('-created_at')
    
    # 按状态分组
    draft_count = initiated_approvals.filter(status='draft').count()
    pending_count = initiated_approvals.filter(status='pending').count()
    approved_count = initiated_approvals.filter(status='approved').count()
    rejected_count = initiated_approvals.filter(status='rejected').count()
    
    context = {
        'initiated_approvals': initiated_approvals,
        'draft_count': draft_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'title': '我发起的审批',
    }
    
    return render(request, 'contract_management/my_initiated_approvals.html', context)
