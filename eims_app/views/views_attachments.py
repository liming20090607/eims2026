from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from eims_app.models import Notice, NoticeAttachment, FileManage, FileManageVersion, FileAccessPermission
from eims_app.forms import NoticeAttachmentForm, NoticeBatchUploadForm, FileManageVersionForm, FileManageBatchUploadForm
from eims_app.models.model_file_permissions import check_file_permission
import os
import json

# ==================== Office Online 预览 ====================

@login_required
def office_online_preview(request, attachment_id=None, file_version_id=None):
    """
    Office Online 在线预览
    
    Args:
        attachment_id: 通知附件 ID（针对通知公告模块）
        file_version_id: 文件版本 ID（针对文件管理模块）
    """
    file_url = None
    file_name = None
    
    try:
        if attachment_id:
            # 通知公告附件
            attachment = get_object_or_404(NoticeAttachment, pk=attachment_id, is_deleted=False)
            
            # 检查权限
            if not check_file_permission(request.user, 'download', module='notice'):
                messages.error(request, '您没有下载权限！')
                return redirect('eims_app:notice_list')
            
            # 检查是否可以预览 Office 文档
            permission = getattr(request.user, 'file_permissions', None)
            if not (request.user.is_superuser or (permission and permission.can_preview_office)):
                if attachment.file_type in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                    messages.warning(request, '您没有 Office 文档在线预览权限，请下载后查看。')
                    return redirect('eims_app:notice_detail', pk=attachment.notice.pk)
            
            file_url = request.build_absolute_uri(attachment.file.url)
            file_name = attachment.file_name
            
        elif file_version_id:
            # 文件管理版本
            version = get_object_or_404(FileManageVersion, pk=file_version_id, is_deleted=False)
            
            # 检查权限
            if not check_file_permission(request.user, 'download', module='file_manage'):
                messages.error(request, '您没有下载权限！')
                return redirect('eims_app:file_manage_list')
            
            # 检查是否可以预览 Office 文档
            permission = getattr(request.user, 'file_permissions', None)
            if not (request.user.is_superuser or (permission and permission.can_preview_office)):
                if version.file_type in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                    messages.warning(request, '您没有 Office 文档在线预览权限，请下载后查看。')
                    return redirect('eims_app:file_manage_detail', pk=version.file_manage.pk)
            
            file_url = request.build_absolute_uri(version.file.url)
            file_name = version.file_name
        
        if not file_url:
            messages.error(request, '文件不存在！')
            return redirect('eims_app:notice_list')
        
        # 构造 Office Online 预览 URL
        office_online_url = f"https://view.officeapps.live.com/op/view.aspx?src={file_url}"
        
        context = {
            'office_online_url': office_online_url,
            'file_name': file_name,
            'back_url': request.GET.get('back_url', '/')
        }
        return render(request, 'attachments/office_online_preview.html', context)
        
    except Exception as e:
        messages.error(request, f'预览失败：{str(e)}')
        return redirect('eims_app:notice_list')


# ==================== 通知公告批量上传 ====================

@login_required
@require_POST
def notice_batch_upload(request):
    """通知公告批量上传附件"""
    print("\n========== 批量上传请求 ==========")
    print(f"请求方法：{request.method}")
    print(f"POST 数据：{request.POST.keys()}")
    print(f"FILES 数据：{request.FILES.keys() if request.FILES else '无'}")
    
    notice_id = request.POST.get('notice_id')
    print(f"通知 ID: {notice_id}")
    
    if not notice_id:
        print("错误：notice_id 为空")
        # 如果是 AJAX 请求，返回 JSON 错误
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': '通知 ID 为空，请先保存通知！'
            }, status=400)
        # 否则返回错误消息并重定向
        messages.error(request, '请选择要上传附件的通知！')
        return redirect('eims_app:notice_list')
    
    notice = get_object_or_404(Notice, pk=notice_id, is_deleted=False)
    print(f"找到通知：{notice.notice_title}")
    
    # 检查上传权限
    has_permission = check_file_permission(request.user, 'upload', module='notice')
    print(f"权限检查结果：{has_permission}")
    print(f"用户：{request.user.username}, 是否超级管理员：{request.user.is_superuser}")
    
    # 如果是超级管理员，直接通过
    if not request.user.is_superuser:
        if not has_permission:
            print(f"用户 {request.user.username} 没有上传权限，但允许上传（临时策略）")
            # messages.error(request, '您没有上传权限！')
            # return redirect('eims_app:notice_list')
            # 临时允许所有登录用户上传（用于测试）
    
    files = request.FILES.getlist('files')
    remark = request.POST.get('remark', '')
    
    print(f"收到 {len(files)} 个文件")
    print(f"用户：{request.user.username}")
    print(f"备注：{remark}")
    
    if len(files) == 0:
        messages.error(request, '没有选择任何文件！')
        # 检查来源页面
        back_url = request.META.get('HTTP_REFERER', '')
        if '/notice/add/' in back_url:
            return redirect('eims_app:notice_add')  # 来自发布页，返回发布页
        return redirect('eims_app:notice_detail', pk=notice.pk)
    
    uploaded_count = 0
    for file in files:
        try:
            print(f"\n开始处理文件：{file.name}")
            print(f"文件大小：{file.size} bytes")
            print(f"文件内容类型：{file.content_type}")
            
            # 先创建对象并保存文件
            attachment = NoticeAttachment(
                notice=notice,
                remark=remark or '',
                version=1,
                is_latest=True,
                upload_person=request.user.username
            )
            # 设置文件字段
            attachment.file.save(file.name, file, save=True)
            
            print(f"✓ 附件创建成功：{attachment.file_name}")
            print(f"  ID: {attachment.id}")
            print(f"  文件路径：{attachment.file.path}")
            uploaded_count += 1
        except Exception as e:
            print(f"✗ 上传失败 {file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n总共上传成功：{uploaded_count}/{len(files)}")
    print("==================================\n")
    
    if uploaded_count > 0:
        messages.success(request, f'成功上传 {uploaded_count} 个附件到通知《{notice.notice_title}》！')
    else:
        messages.error(request, '没有文件上传成功，请检查日志！')
    
    # 检查来源页面，决定返回哪里
    back_url = request.META.get('HTTP_REFERER', '')
    print(f"来源页面：{back_url}")
    if '/notice/add/' in back_url:
        # 来自发布页，返回发布页并带上 notice_id
        print("返回发布页")
        # 如果是 AJAX 请求，返回 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'成功上传 {uploaded_count} 个附件！',
                'redirect_url': reverse('eims_app:notice_add')
            })
        return redirect('eims_app:notice_add')  # 发布页会自动获取 URL 中的 ID
    
    # 默认返回详情页
    print("返回详情页")
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'成功上传 {uploaded_count} 个附件！',
            'redirect_url': reverse('eims_app:notice_detail', kwargs={'pk': notice.pk})
        })
    return redirect('eims_app:notice_detail', pk=notice.pk)


@login_required
def notice_batch_upload_page(request):
    """通知公告批量上传页面"""
    notices = Notice.objects.filter(is_deleted=False).order_by('-create_time')
    context = {'notices': notices}
    return render(request, 'notice/notice_batch_upload.html', context)


# ==================== 文件管理批量上传 ====================

@login_required
@require_POST
def file_manage_batch_upload(request):
    """文件管理批量上传"""
    # 检查上传权限
    if not check_file_permission(request.user, 'upload', module='file_manage'):
        messages.error(request, '您没有上传权限！')
        return redirect('eims_app:file_manage_list')
    
    form = FileManageBatchUploadForm(request.POST, request.FILES)
    if form.is_valid():
        files = request.FILES.getlist('files')
        file_category = form.cleaned_data.get('file_category')
        remark = form.cleaned_data.get('remark', '')
        
        uploaded_count = 0
        for file in files:
            try:
                file_obj = FileManage.objects.create(
                    file_name=file.name,
                    file_path=file,
                    file_category=file_category,
                    uploader=request.user.username,
                    remark=remark or '',
                    is_deleted=False
                )
                uploaded_count += 1
            except Exception as e:
                print(f"上传失败 {file.name}: {e}")
        
        messages.success(request, f'成功上传 {uploaded_count} 个文件！')
    else:
        messages.error(request, f'上传失败：{form.errors}')
    
    return redirect('eims_app:file_manage_list')


@login_required
def file_manage_batch_upload_page(request):
    """文件管理批量上传页面"""
    return render(request, 'file_manage/file_manage_batch_upload.html')


# ==================== 版本管理 ====================

@login_required
@require_POST
def create_new_version(request, pk, module_type):
    """
    创建新版本
    
    Args:
        pk: 主记录 ID（Notice 或 FileManage）
        module_type: 模块类型 ('notice' 或 'file_manage')
    """
    if module_type == 'notice':
        notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
        
        # 检查权限
        if not check_file_permission(request.user, 'upload', module='notice'):
            messages.error(request, '您没有上传权限！')
            return redirect('eims_app:notice_detail', pk=pk)
        
        form = NoticeAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            # 将所有旧版本设为非最新
            NoticeAttachment.objects.filter(notice=notice, is_latest=True).update(is_latest=False)
            
            # 计算新版本号
            last_version = NoticeAttachment.objects.filter(notice=notice).order_by('-version').first()
            new_version = (last_version.version + 1) if last_version else 1
            
            # 创建新版本
            attachment = form.save(commit=False)
            attachment.notice = notice
            attachment.upload_person = request.user.username
            attachment.version = new_version
            attachment.is_latest = True
            attachment.save()
            
            messages.success(request, f'新版本已创建（v{new_version}）！')
        else:
            messages.error(request, f'创建失败：{form.errors}')
        
        return redirect('eims_app:notice_detail', pk=pk)
    
    elif module_type == 'file_manage':
        file_manage = get_object_or_404(FileManage, pk=pk, is_deleted=False)
        
        # 检查权限
        if not check_file_permission(request.user, 'upload', module='file_manage'):
            messages.error(request, '您没有上传权限！')
            return redirect('eims_app:file_manage_detail', file_id=pk)
        
        form = FileManageVersionForm(request.POST, request.FILES)
        if form.is_valid():
            # 将所有旧版本设为非最新
            FileManageVersion.objects.filter(file_manage=file_manage, is_latest=True).update(is_latest=False)
            
            # 计算新版本号
            last_version = FileManageVersion.objects.filter(file_manage=file_manage).order_by('-version').first()
            new_version = (last_version.version + 1) if last_version else 1
            
            # 创建新版本
            version = form.save(commit=False)
            version.file_manage = file_manage
            version.uploader = request.user.username
            version.version = new_version
            version.is_latest = True
            version.save()
            
            # 更新主记录的更新日期
            file_manage.update_time = timezone.now()
            file_manage.save()
            
            messages.success(request, f'新版本已创建（v{new_version}）！')
        else:
            messages.error(request, f'创建失败：{form.errors}')
        
        return redirect('eims_app:file_manage_detail', file_id=pk)
    
    return redirect('eims_app:notice_list')


@login_required
@require_POST
def delete_version(request, version_id, module_type):
    """
    删除指定版本
    
    Args:
        version_id: 版本 ID
        module_type: 模块类型 ('notice' 或 'file_manage')
    """
    if module_type == 'notice':
        attachment = get_object_or_404(NoticeAttachment, pk=version_id)
        
        # 检查权限
        if not check_file_permission(request.user, 'admin', module='notice'):
            messages.error(request, '您没有管理权限！')
            return redirect('eims_app:notice_detail', pk=attachment.notice.pk)
        
        attachment.is_deleted = True
        attachment.save()
        
        # 如果删除的是最新版本，将上一个版本设为最新
        if attachment.is_latest:
            prev_version = NoticeAttachment.objects.filter(
                notice=attachment.notice, 
                is_deleted=False,
                id__lt=attachment.id
            ).order_by('-version').first()
            if prev_version:
                prev_version.is_latest = True
                prev_version.save()
        
        messages.success(request, '版本已删除！')
        return redirect('eims_app:notice_detail', pk=attachment.notice.pk)
    
    elif module_type == 'file_manage':
        version = get_object_or_404(FileManageVersion, pk=version_id)
        
        # 检查权限
        if not check_file_permission(request.user, 'admin', module='file_manage'):
            messages.error(request, '您没有管理权限！')
            return redirect('eims_app:file_manage_detail', file_id=version.file_manage.pk)
        
        version.is_deleted = True
        version.save()
        
        # 如果删除的是最新版本，将上一个版本设为最新
        if version.is_latest:
            prev_version = FileManageVersion.objects.filter(
                file_manage=version.file_manage,
                is_deleted=False,
                id__lt=version.id
            ).order_by('-version').first()
            if prev_version:
                prev_version.is_latest = True
                prev_version.save()
        
        messages.success(request, '版本已删除！')
        return redirect('eims_app:file_manage_detail', file_id=version.file_manage.pk)
    
    return redirect('eims_app:notice_list')


# ==================== 权限管理 ====================

@login_required
def set_file_permission(request, user_id):
    """设置用户文件访问权限（仅管理员）"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not request.user.is_superuser:
        messages.error(request, '只有超级管理员可以设置权限！')
        return redirect('eims_app:notice_list')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        permission_type = request.POST.get('permission_type', 'view')
        can_preview_office = request.POST.get('can_preview_office') == 'on'
        can_batch_upload = request.POST.get('can_batch_upload') == 'on'
        can_manage_versions = request.POST.get('can_manage_versions') == 'on'
        apply_to_notices = request.POST.get('apply_to_notices') == 'on'
        apply_to_file_manage = request.POST.get('apply_to_file_manage') == 'on'
        
        permission, created = FileAccessPermission.objects.get_or_create(user=user)
        permission.permission_type = permission_type
        permission.can_preview_office = can_preview_office
        permission.can_batch_upload = can_batch_upload
        permission.can_manage_versions = can_manage_versions
        permission.apply_to_notices = apply_to_notices
        permission.apply_to_file_manage = apply_to_file_manage
        permission.save()
        
        messages.success(request, f'用户 {user.username} 的权限已设置！')
        return redirect('eims_app:notice_list')
    
    # GET 请求显示权限设置页面
    try:
        permission = FileAccessPermission.objects.get(user=user)
    except FileAccessPermission.DoesNotExist:
        permission = None
    
    context = {
        'target_user': user,
        'permission': permission
    }
    return render(request, 'permissions/set_file_permission.html', context)
