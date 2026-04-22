from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.db.models import Q


@login_required
def archive_approval_chain(request):
    """归档审批流程列表"""
    from eims_app.models.model_archive_approval import ArchiveApproval
    
    # 获取筛选参数
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    
    # 基础查询集
    queryset = ArchiveApproval.objects.select_related('applicant', 'department', 'current_approver').all()
    
    # 筛选
    if status:
        queryset = queryset.filter(status=status)
    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword) |
            Q(project_name__icontains=keyword) |
            Q(project_code__icontains=keyword)
        )
    
    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'keyword': keyword,
        'APPROVAL_STATUS_CHOICES': ArchiveApproval.APPROVAL_STATUS_CHOICES,
    }
    
    return render(request, 'archive_management/approval_chain_list.html', context)


@login_required
def archive_approval_add(request):
    """新增归档审批 - 必须上传附件"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveAttachment
    from eims_app.forms.form_archive_approval import ArchiveApprovalForm, ArchiveAttachmentForm
    from django.utils import timezone
    
    if request.method == 'POST':
        form = ArchiveApprovalForm(request.POST)
        
        # 检查是否上传了附件（新增时必须上传）
        files = request.FILES.getlist('new_attachments')
        if not files or len(files) == 0:
            messages.error(request, '⚠️ 请至少上传一个附件才能提交')
            return render(request, 'archive_management/approval_form.html', {
                'form': form,
                'title': '新增归档审批',
            })
        
        if form.is_valid():
            # 保存审批信息
            approval = form.save(commit=False)
            approval.applicant = request.user
            approval.status = 'draft'  # 默认为草稿
            approval.save()
            
            # 处理文件上传
            file_types = request.POST.getlist('new_file_types')
            pages_list = request.POST.getlist('new_pages')
            document_dates = request.POST.getlist('new_document_dates')
            remarks_list = request.POST.getlist('new_remarks')
            
            for i, file in enumerate(files):
                attachment = ArchiveAttachment(
                    approval=approval,
                    file=file,
                    file_type=file_types[i] if i < len(file_types) else 'contract',
                    pages=int(pages_list[i]) if i < len(pages_list) and pages_list[i] else 0,
                    document_date=document_dates[i] if i < len(document_dates) and document_dates[i] else None,
                    remark=remarks_list[i] if i < len(remarks_list) else ''
                )
                attachment.save()
            
            messages.success(request, '归档审批创建成功！')
            return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    else:
        form = ArchiveApprovalForm()
    
    context = {
        'form': form,
        'title': '新增归档审批',
    }
    
    return render(request, 'archive_management/approval_form.html', context)


@login_required
def archive_approval_detail(request, pk):
    """归档审批详情"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveApprovalRecord
    from django.contrib.auth import get_user_model
    
    approval = get_object_or_404(ArchiveApproval, pk=pk)
    
    # 获取审批历史记录
    records = approval.approval_records.select_related('operator').all()
    
    # 获取未删除的附件列表
    attachments = approval.attachments.filter(is_deleted=False)
    
    # 获取可用的审批人列表（用于转发功能）
    User = get_user_model()
    available_approvers = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
    
    context = {
        'approval': approval,
        'records': records,
        'attachments': attachments,
        'available_approvers': available_approvers,
        'title': '归档审批详情',
    }
    
    return render(request, 'archive_management/approval_detail.html', context)


@login_required
def archive_approval_edit(request, pk):
    """编辑归档审批（草稿、已退回或已撤回状态可编辑，且仅申请人可编辑）"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveAttachment
    from eims_app.forms.form_archive_approval import ArchiveApprovalForm, ArchiveAttachmentForm
    
    approval = get_object_or_404(ArchiveApproval, pk=pk)
    
    # 只有申请人可以编辑
    if approval.applicant != request.user:
        messages.error(request, '只有发起人可以编辑该审批')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 草稿、已退回或已撤回状态可以编辑
    if approval.status not in ['draft', 'rejected', 'cancelled']:
        messages.error(request, '只有草稿、已退回或已撤回状态的审批可以编辑')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 获取已有附件
    existing_attachments = approval.attachments.filter(is_deleted=False)
    
    if request.method == 'POST':
        form = ArchiveApprovalForm(request.POST, instance=approval)
        if form.is_valid():
            approval = form.save()
            
            # 处理附件：删除旧附件（如果用户勾选了删除），添加新附件
            # 删除操作
            delete_ids = request.POST.getlist('delete_attachments')
            if delete_ids:
                ArchiveAttachment.objects.filter(
                    id__in=delete_ids, 
                    approval=approval
                ).update(is_deleted=True)
            
            # 上传新附件
            new_files = request.FILES.getlist('new_attachments')
            if new_files:
                file_types = request.POST.getlist('new_file_types')
                pages_list = request.POST.getlist('new_pages')
                document_dates = request.POST.getlist('new_document_dates')
                remarks_list = request.POST.getlist('new_remarks')
                
                for i, file in enumerate(new_files):
                    attachment = ArchiveAttachment(
                        approval=approval,
                        file=file,
                        file_type=file_types[i] if i < len(file_types) else 'contract',
                        pages=int(pages_list[i]) if i < len(pages_list) and pages_list[i] else 0,
                        document_date=document_dates[i] if i < len(document_dates) and document_dates[i] else None,
                        remark=remarks_list[i] if i < len(remarks_list) else ''
                    )
                    attachment.save()
            
            messages.success(request, '归档审批更新成功！')
            return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    else:
        form = ArchiveApprovalForm(instance=approval)
    
    context = {
        'form': form,
        'approval': approval,
        'existing_attachments': existing_attachments,
        'title': '编辑归档审批',
    }
    
    return render(request, 'archive_management/approval_form.html', context)


@login_required
def archive_approval_submit(request, pk):
    """提交归档审批"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveApprovalRecord
    from django.utils import timezone
    
    approval = get_object_or_404(ArchiveApproval, pk=pk)
    
    # 权限检查：只有申请人可以提交
    if approval.applicant != request.user:
        messages.error(request, '只有申请人可以提交审批')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 状态检查：只有草稿、已退回或已撤回状态可以提交
    if approval.status not in ['draft', 'rejected', 'cancelled']:
        messages.error(request, '当前状态不允许提交')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 检查是否有附件
    if not approval.attachments.filter(is_deleted=False).exists():
        messages.error(request, '请至少上传一个附件')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 更新状态
    approval.status = 'pending'
    approval.submitted_at = timezone.now()
    approval.initiator = request.user
    approval.initiation_time = timezone.now()
    
    # 指派审批人
    approval.assign_current_approver()
    approval.save()
    
    # 记录操作
    record = ArchiveApprovalRecord(
        approval=approval,
        action='submit',
        operator=request.user,
        comment='提交审批'
    )
    record.save()
    
    messages.success(request, '归档审批已提交')
    return redirect('eims_app:archive_approval_detail', pk=approval.pk)


@login_required
def archive_approval_approve(request, pk):
    """同意归档审批 - 可选择终结审批或后续审批"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveApprovalRecord
    from django.utils import timezone
    
    approval = get_object_or_404(ArchiveApproval, pk=pk)
    
    # 权限检查：只有当前审批人可以审批
    if approval.current_approver != request.user:
        messages.error(request, '您不是当前审批人')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 状态检查
    if approval.status not in ['pending', 'reviewing']:
        messages.error(request, '当前状态不允许审批')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    comment = request.POST.get('comment', '')
    action_type = request.POST.get('action_type', 'finalize')  # 'forward' 或 'finalize'
    
    if action_type == 'forward':
        # 后续审批 - 流转到下一级
        assign_method = request.POST.get('assign_method', 'auto')  # 'auto' 或 'manual'
        
        if assign_method == 'manual':
            # 自主选择审批人
            next_approver_id = request.POST.get('next_approver')
            if next_approver_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    next_approver = User.objects.get(pk=next_approver_id)
                    # 升级审批级别
                    approval.approval_level += 1
                    approval.current_approver = next_approver
                    approval.save()
                    
                    # 记录操作
                    ArchiveApprovalRecord.objects.create(
                        approval=approval,
                        action='approve',
                        operator=request.user,
                        comment=comment or f'同意并转发给 {next_approver.username}'
                    )
                    
                    messages.success(request, f'已转发给 {next_approver.username} 进行下一步审批')
                except User.DoesNotExist:
                    messages.error(request, '选择的审批人不存在')
                    return redirect('eims_app:archive_approval_detail', pk=approval.pk)
            else:
                messages.error(request, '请选择下一步审批人')
                return redirect('eims_app:archive_approval_detail', pk=approval.pk)
        else:
            # 系统指定审批人 - 根据流程自动指派
            try:
                # 升级审批级别
                approval.approval_level += 1
                assigned_approver = approval.assign_current_approver()
                
                if assigned_approver:
                    approval.save()
                    
                    # 记录操作
                    ArchiveApprovalRecord.objects.create(
                        approval=approval,
                        action='approve',
                        operator=request.user,
                        comment=comment or f'同意并由系统指派给 {assigned_approver.username}'
                    )
                    
                    messages.success(request, f'审批通过，系统已指派给 {assigned_approver.username} 进行下一步审批')
                else:
                    messages.warning(request, '未找到合适的下一位审批人，请手动选择或联系管理员配置')
                    return redirect('eims_app:archive_approval_detail', pk=approval.pk)
            except Exception as e:
                messages.error(request, f'系统指派审批人失败：{str(e)}')
                return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    else:
        # 终结审批
        approval.status = 'approved'
        approval.approved_at = timezone.now()
        approval.approval_result = 'archived'
        approval.current_approver = None
        approval.save()
        
        # 记录操作
        ArchiveApprovalRecord.objects.create(
            approval=approval,
            action='approve',
            operator=request.user,
            comment=comment or '同意'
        )
        
        messages.success(request, '归档审批已通过')
    
    return redirect('eims_app:archive_approval_detail', pk=approval.pk)


@login_required
def archive_approval_reject(request, pk):
    """退回归档审批"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveApprovalRecord
    
    approval = get_object_or_404(ArchiveApproval, pk=pk)
    
    # 权限检查：只有当前审批人可以退回
    if approval.current_approver != request.user:
        messages.error(request, '您不是当前审批人')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 状态检查
    if approval.status not in ['pending', 'reviewing']:
        messages.error(request, '当前状态不允许退回')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    comment = request.POST.get('comment', '')
    if not comment:
        messages.error(request, '退回时必须填写退回原因')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 更新状态
    approval.status = 'rejected'
    approval.current_approver = None
    approval.save()
    
    # 记录操作
    record = ArchiveApprovalRecord(
        approval=approval,
        action='reject',
        operator=request.user,
        comment=comment
    )
    record.save()
    
    messages.success(request, '审批已退回')
    return redirect('eims_app:archive_approval_detail', pk=approval.pk)


@login_required
def archive_approval_cancel(request, pk):
    """撤销归档审批"""
    from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveApprovalRecord
    
    approval = get_object_or_404(ArchiveApproval, pk=pk)
    
    # 权限检查：只有申请人可以撤销
    if approval.applicant != request.user:
        messages.error(request, '只有申请人可以撤销审批')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    # 状态检查：只有待审核和审核中可以撤销
    if approval.status not in ['pending', 'reviewing']:
        messages.error(request, '当前状态不允许撤销')
        return redirect('eims_app:archive_approval_detail', pk=approval.pk)
    
    comment = request.POST.get('comment', '')
    
    # 更新状态
    approval.status = 'cancelled'
    approval.current_approver = None
    approval.save()
    
    # 记录操作
    record = ArchiveApprovalRecord(
        approval=approval,
        action='cancel',
        operator=request.user,
        comment=comment
    )
    record.save()
    
    messages.success(request, '审批已撤销')
    return redirect('eims_app:archive_approval_detail', pk=approval.pk)
