from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from eims_app.models.model_contract_approval import ContractApproval
from eims_app.models.model_seal_approval import SealApproval
from eims_app.models.model_archive_approval import ArchiveApproval


@login_required
def my_pending_approvals(request):
    """我的待审批列表 - 包含合同审批、用印审批、归档审批"""
    
    # 获取当前用户待审批的所有审批事项
    contract_approvals = ContractApproval.objects.filter(
        current_approver=request.user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).select_related('applicant', 'department').order_by('-created_at')
    
    seal_approvals = SealApproval.objects.filter(
        current_approver=request.user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).select_related('applicant', 'department').order_by('-created_at')
    
    archive_approvals = ArchiveApproval.objects.filter(
        current_approver=request.user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).select_related('applicant', 'department').order_by('-created_at')
    
    # 合并所有审批事项，添加审批类型标识
    all_approvals = []
    
    for approval in contract_approvals:
        all_approvals.append({
            'id': approval.pk,
            'approval_type': 'contract',
            'type_display': '合同审批',
            'title': approval.title,
            'subtitle': approval.contract_name,
            'applicant': approval.applicant,
            'department': approval.department,
            'status': approval.status,
            'submitted_at': approval.submitted_at,
            'created_at': approval.created_at,
            'detail_url': 'eims_app:contract_approval_detail',
        })
    
    for approval in seal_approvals:
        all_approvals.append({
            'id': approval.pk,
            'approval_type': 'seal',
            'type_display': '用印审批',
            'title': approval.title,
            'subtitle': f'{approval.document_name} ({approval.get_seal_type_display()})',
            'applicant': approval.applicant,
            'department': approval.department,
            'status': approval.status,
            'submitted_at': approval.submitted_at,
            'created_at': approval.created_at,
            'detail_url': 'eims_app:seal_approval_detail',
        })
    
    for approval in archive_approvals:
        all_approvals.append({
            'id': approval.pk,
            'approval_type': 'archive',
            'type_display': '归档审批',
            'title': approval.title,
            'subtitle': approval.project_name,
            'applicant': approval.applicant,
            'department': approval.department,
            'status': approval.status,
            'submitted_at': approval.submitted_at,
            'created_at': approval.created_at,
            'detail_url': 'eims_app:archive_approval_detail',
        })
    
    # 按创建时间排序
    all_approvals.sort(key=lambda x: x['created_at'], reverse=True)
    
    # 统计数量
    total_count = len(all_approvals)
    contract_count = len([a for a in all_approvals if a['approval_type'] == 'contract'])
    seal_count = len([a for a in all_approvals if a['approval_type'] == 'seal'])
    archive_count = len([a for a in all_approvals if a['approval_type'] == 'archive'])
    
    # 按状态分组统计
    pending_count = len([a for a in all_approvals if a['status'] == 'pending'])
    reviewing_count = len([a for a in all_approvals if a['status'] == 'reviewing'])
    
    context = {
        'pending_approvals': all_approvals,
        'total_count': total_count,
        'contract_count': contract_count,
        'seal_count': seal_count,
        'archive_count': archive_count,
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
