from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
import os
from eims_app.models.model_seal_approval import SealApproval, SealAttachment, SealApprovalRecord
from eims_app.forms.form_seal_approval import SealApprovalForm, SealAttachmentForm
from eims_app.utils.tenant_utils import filter_queryset_by_tenant
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def seal_approval_list(request):
    """用印审批列表"""
    # 获取搜索参数
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # 基础查询
    approvals = SealApproval.objects.filter(is_deleted=False)
    
    # 应用租户过滤
    approvals = filter_queryset_by_tenant(approvals, request)
    
    # 搜索过滤
    if search_query:
        approvals = approvals.filter(
            Q(title__icontains=search_query) |
            Q(document_name__icontains=search_query) |
            Q(applicant__username__icontains=search_query)
        )
    
    # 状态过滤
    if status_filter:
        approvals = approvals.filter(status=status_filter)
    
    # 排序
    approvals = approvals.order_by('-created_at')
    
    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(approvals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'title': '用印审批列表',
    }
    
    return render(request, 'seal_management/approval_chain_list.html', context)


@login_required
def seal_approval_add(request):
    """新增用印审批 - 必须上传附件"""
    if request.method == 'POST':
        form = SealApprovalForm(request.POST)
        
        # 检查是否上传了附件（新增时必须上传）
        files = request.FILES.getlist('new_attachments')
        if not files or len(files) == 0:
            messages.error(request, '⚠️ 请至少上传一个附件才能提交')
            return render(request, 'seal_management/approval_form.html', {
                'form': form,
                'title': '新增用印审批',
            })
        
        if form.is_valid():
            # 保存审批信息
            approval = form.save(commit=False)
            approval.applicant = request.user
            approval.status = 'draft'  # 默认为草稿
            approval.save()
            
            # 处理文件上传
            file_types = request.POST.getlist('new_file_types')
            
            for i, file in enumerate(files):
                attachment = SealAttachment(
                    approval=approval,
                    file=file,
                    file_type=file_types[i] if i < len(file_types) else 'document'
                )
                attachment.save()
            
            messages.success(request, '用印审批创建成功！')
            return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    else:
        form = SealApprovalForm()
    
    context = {
        'form': form,
        'title': '新增用印审批',
    }
    
    return render(request, 'seal_management/approval_form.html', context)


@login_required
def seal_approval_detail(request, pk):
    """用印审批详情"""
    approval = get_object_or_404(SealApproval, pk=pk)
    
    # 获取审批历史记录
    records = approval.approval_records.select_related('operator').all()
    
    # 获取附件
    attachments = approval.attachments.filter(is_deleted=False)
    
    # 获取可用的审批人列表（用于转发功能）
    available_approvers = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
    
    context = {
        'approval': approval,
        'records': records,
        'attachments': attachments,
        'available_approvers': available_approvers,
        'title': '用印审批详情',
    }
    
    return render(request, 'seal_management/approval_detail.html', context)


@login_required
def seal_approval_edit(request, pk):
    """编辑用印审批（草稿、已退回或已撤回状态可编辑，且仅申请人可编辑）"""
    approval = get_object_or_404(SealApproval, pk=pk)
    
    # 只有申请人可以编辑
    if approval.applicant != request.user:
        messages.error(request, '只有发起人可以编辑该审批')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 草稿、已退回或已撤回状态可以编辑
    if approval.status not in ['draft', 'rejected', 'cancelled']:
        messages.error(request, '只有草稿、已退回或已撤回状态的审批可以编辑')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 获取已有附件
    existing_attachments = approval.attachments.filter(is_deleted=False)
    
    if request.method == 'POST':
        form = SealApprovalForm(request.POST, instance=approval)
        if form.is_valid():
            approval = form.save()
            
            # 处理附件：删除旧附件（如果用户勾选了删除），添加新附件
            # 删除操作
            delete_ids = request.POST.getlist('delete_attachments')
            if delete_ids:
                SealAttachment.objects.filter(
                    id__in=delete_ids, 
                    approval=approval
                ).update(is_deleted=True)
            
            # 上传新附件
            new_files = request.FILES.getlist('new_attachments')
            new_file_types = request.POST.getlist('new_file_types')
            
            for i, file in enumerate(new_files):
                attachment = SealAttachment(
                    approval=approval,
                    file=file,
                    file_type=new_file_types[i] if i < len(new_file_types) else 'document'
                )
                attachment.save()
            
            messages.success(request, '用印审批更新成功！')
            return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    else:
        form = SealApprovalForm(instance=approval)
    
    context = {
        'form': form,
        'approval': approval,
        'existing_attachments': existing_attachments,
        'current_time': timezone.now(),
        'title': '编辑用印审批',
    }
    
    return render(request, 'seal_management/approval_form.html', context)


@login_required
def seal_approval_submit(request, pk):
    """提交用印审批"""
    approval = get_object_or_404(SealApproval, pk=pk)
    
    # 只有申请人可以提交
    if approval.applicant != request.user:
        messages.error(request, '只有发起人可以提交该审批')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 只有草稿状态可以提交
    if approval.status != 'draft':
        messages.error(request, '只有草稿状态的审批可以提交')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 检查是否上传了附件
    if not approval.attachments.filter(is_deleted=False).exists():
        messages.error(request, '请至少上传一个附件后再提交')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 更新状态
    approval.status = 'pending'
    approval.submitted_at = timezone.now()
    approval.initiator = request.user
    approval.initiation_time = timezone.now()
    approval.save()
    
    # 记录操作
    SealApprovalRecord.objects.create(
        approval=approval,
        action='submit',
        operator=request.user,
        comment='提交审批'
    )
    
    messages.success(request, '用印审批已提交，等待审核')
    return redirect('eims_app:seal_approval_detail', pk=approval.pk)


@login_required
def seal_approval_approve(request, pk):
    """同意用印审批 - 可选择终结审批或后续审批"""
    approval = get_object_or_404(SealApproval, pk=pk)
    
    # 权限检查
    if approval.current_approver != request.user and not request.user.is_superuser:
        messages.error(request, '您没有权限审批该申请')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 状态检查
    if approval.status not in ['pending', 'reviewing']:
        messages.error(request, '该审批单状态不允许审批')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    comment = request.POST.get('comment', '')
    action_type = request.POST.get('action_type', 'finalize')  # 'forward' 或 'finalize'
    
    # 记录审批操作
    SealApprovalRecord.objects.create(
        approval=approval,
        action='approve',
        operator=request.user,
        comment=comment if comment else '同意'
    )
    
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
                    SealApprovalRecord.objects.create(
                        approval=approval,
                        action='approve',
                        operator=request.user,
                        comment=comment or f'同意并转发给 {next_approver.username}'
                    )
                    
                    messages.success(request, f'已转发给 {next_approver.username} 进行下一步审批')
                except User.DoesNotExist:
                    messages.error(request, '选择的审批人不存在')
                    return redirect('eims_app:seal_approval_detail', pk=approval.pk)
            else:
                messages.error(request, '请选择下一步审批人')
                return redirect('eims_app:seal_approval_detail', pk=approval.pk)
        else:
            # 系统指定审批人 - 根据流程自动指派
            try:
                # 升级审批级别
                approval.approval_level += 1
                assigned_approver = approval.assign_current_approver()
                
                if assigned_approver:
                    approval.save()
                    
                    # 记录操作
                    SealApprovalRecord.objects.create(
                        approval=approval,
                        action='approve',
                        operator=request.user,
                        comment=comment or f'同意并由系统指派给 {assigned_approver.username}'
                    )
                    
                    messages.success(request, f'审批通过，系统已指派给 {assigned_approver.username} 进行下一步审批')
                else:
                    messages.warning(request, '未找到合适的下一位审批人，请手动选择或联系管理员配置')
                    return redirect('eims_app:seal_approval_detail', pk=approval.pk)
            except Exception as e:
                messages.error(request, f'系统指派审批人失败：{str(e)}')
                return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    else:
        # 终结审批
        approval.status = 'approved'
        approval.approved_at = timezone.now()
        approval.current_approver = None
        approval.save()
        
        messages.success(request, '用印审批已通过！')
    
    return redirect('eims_app:seal_approval_detail', pk=approval.pk)


@login_required
def seal_approval_reject(request, pk):
    """退回用印审批"""
    approval = get_object_or_404(SealApproval, pk=pk)
    
    # 权限检查
    if approval.current_approver != request.user and not request.user.is_superuser:
        messages.error(request, '您没有权限审批该申请')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 状态检查
    if approval.status not in ['pending', 'reviewing']:
        messages.error(request, '该审批单状态不允许审批')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    comment = request.POST.get('comment', '')
    if not comment:
        messages.error(request, '退回审批必须填写审批意见')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 记录审批操作
    SealApprovalRecord.objects.create(
        approval=approval,
        action='reject',
        operator=request.user,
        comment=comment
    )
    
    # 更新状态
    approval.status = 'rejected'
    approval.current_approver = None
    approval.save()
    
    messages.success(request, '已退回到发起人')
    return redirect('eims_app:seal_approval_detail', pk=approval.pk)


@login_required
def seal_approval_cancel(request, pk):
    """撤销用印审批（仅发起人可撤销）"""
    approval = get_object_or_404(SealApproval, pk=pk)
    
    # 只有发起人可以撤销
    if approval.applicant != request.user:
        messages.error(request, '只有发起人可以撤销该审批')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 只有草稿、待审核或审核中状态可以撤销
    if approval.status not in ['draft', 'pending', 'reviewing']:
        messages.error(request, '当前状态不允许撤销')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    comment = request.POST.get('comment', '')
    
    # 记录撤销操作
    SealApprovalRecord.objects.create(
        approval=approval,
        action='cancel',
        operator=request.user,
        comment=comment if comment else '撤销审批'
    )
    
    # 更新状态
    approval.status = 'cancelled'
    approval.current_approver = None
    approval.save()
    
    messages.success(request, '已撤销用印审批')
    return redirect('eims_app:seal_approval_detail', pk=approval.pk)


@login_required
def seal_approval_delete_attachment(request, attachment_id):
    """删除用印审批附件"""
    attachment = get_object_or_404(SealAttachment, pk=attachment_id)
    approval = attachment.approval
    
    # 权限检查：只有申请人或超级管理员可以删除
    if approval.applicant != request.user and not request.user.is_superuser:
        messages.error(request, '您没有权限删除该附件')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 只有草稿、已退回或已撤回状态可以删除附件
    if approval.status not in ['draft', 'rejected', 'cancelled']:
        messages.error(request, '当前状态不允许删除附件')
        return redirect('eims_app:seal_approval_detail', pk=approval.pk)
    
    # 软删除
    attachment.is_deleted = True
    attachment.save()
    
    messages.success(request, '附件已删除')
    return redirect('eims_app:seal_approval_detail', pk=approval.pk)


@login_required
def get_department_personnel_ajax(request):
    """获取指定部门的人员列表（AJAX）"""
    department_id = request.GET.get('department_id')
    
    if not department_id:
        return JsonResponse({'success': False, 'message': '缺少部门ID'})
    
    try:
        from eims_app.models.model_department import Department
        from eims_app.models.model_personnel import Personnel
        
        # 获取部门
        department = Department.objects.get(pk=department_id, is_deleted=False)
        
        # 获取该部门的所有人员（从Personnel表，通过department字段匹配）
        personnel_filter = {
            'department': department.department_name,
            'is_deleted': False
        }
        if hasattr(request, 'tenant') and request.tenant:
            personnel_filter['tenant_id'] = request.tenant.id
        
        personnel_list = Personnel.objects.filter(**personnel_filter).order_by('name').values('id', 'name', 'personnel_code')
        
        personnel_data = list(personnel_list)
        
        return JsonResponse({
            'success': True,
            'personnel': personnel_data
        })
    except Department.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '部门不存在'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def seal_attachment_preview(request, attachment_id):
    """用印审批附件预览"""
    attachment = get_object_or_404(SealAttachment, pk=attachment_id, is_deleted=False)
    
    # 获取文件扩展名
    file_name = attachment.file_name
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # 构建文件URL
    file_url = request.build_absolute_uri(attachment.file.url)
    
    context = {
        'attachment': attachment,
        'file_name': file_name,
        'file_url': file_url,
        'file_ext': file_ext,
        'back_url': request.GET.get('back_url', '')
    }
    
    # 根据文件类型返回不同的预览模板
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        # 图片类型
        return render(request, 'seal_management/attachment_preview_image.html', context)
    elif file_ext == '.pdf':
        # PDF类型
        return render(request, 'seal_management/attachment_preview_pdf.html', context)
    elif file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
        # Office文档类型 - 由于本地服务器无法被Office Online访问，直接提示下载
        messages.info(request, f'Office文档（{file_ext}）需要联网且文件可公网访问才能在线预览。当前为本地服务器，请下载后使用本地Office软件打开。')
        return redirect('eims_app:seal_attachment_download', attachment_id=attachment_id)
    else:
        # 其他类型不支持预览，提示下载
        messages.info(request, '该文件类型不支持在线预览，请下载后查看！')
        return redirect('eims_app:seal_attachment_download', attachment_id=attachment_id)


@login_required
def seal_attachment_download(request, attachment_id):
    """用印审批附件下载"""
    from django.http import FileResponse
    from django.utils.encoding import escape_uri_path
    
    attachment = get_object_or_404(SealAttachment, pk=attachment_id, is_deleted=False)
    
    # 打开文件
    file_obj = attachment.file.open('rb')
    
    # 构建响应
    response = FileResponse(file_obj)
    
    # 设置响应头，指定下载文件名（处理中文文件名）
    encoded_filename = escape_uri_path(attachment.file_name)
    response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    
    return response
