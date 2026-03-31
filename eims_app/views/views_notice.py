 

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from eims_app.models import Notice
from eims_app.forms import NoticeForm

# 通知公告列表（优化版 - 含关键字、上传人、文件预览）
@login_required
def notice_list(request):
    search_key = request.GET.get('search', '')
    keywords = request.GET.get('keywords', '')
    notice_status = request.GET.get('notice_status', '')
    notice_type = request.GET.get('notice_type', '')

    notices = Notice.objects.filter(is_deleted=False)
    
    # 关键词筛选（通知标题、关键字、发布人、上传人、内容摘要）
    if search_key:
        notices = notices.filter(
            Q(notice_title__icontains=search_key) | 
            Q(keywords__icontains=search_key) |
            Q(publish_person__icontains=search_key) |
            Q(upload_person__icontains=search_key) |
            Q(notice_content__icontains=search_key)
        )
    
    # 关键字筛选
    if keywords:
        notices = notices.filter(keywords__icontains=keywords)
    
    # 类型筛选
    if notice_type:
        notices = notices.filter(notice_type=notice_type)
    
    # 状态筛选（草稿/已发布/已撤回）
    if notice_status:
        notices = notices.filter(notice_status=notice_status)

    # 分页配置（10 条/页，按创建时间倒序）
    page = request.GET.get('page', 1)
    from django.core.paginator import Paginator
    paginator = Paginator(notices.order_by('-create_time'), 10)
    notices = paginator.get_page(page)

    back_url = request.META.get('HTTP_REFERER', '/')
    context = {
        'notices': notices,
        'search_key': search_key,
        'keywords': keywords,
        'notice_status': notice_status,
        'notice_type': notice_type,
        'back_url': back_url,
        'active_menu': 'notice'
    }
    return render(request, 'notice/notice_list.html', context)

# 通知公告详情
@login_required
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
    back_url = request.GET.get('back_url', '/notice/list/')
    context = {
        'notice': notice,
        'back_url': back_url,
        'active_menu': 'notice'
    }
    return render(request, 'notice/notice_detail.html', context)

# 添加通知公告（优化版 - 必填标题和关键字）
@login_required
def notice_add(request, pk=None):
    # 如果有 pk 参数，说明是已保存的通知，可以获取通知对象
    if pk:
        notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
        # 可以预填充一些数据
    
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            # 自动填充发布人和上传人（当前登录用户）
            notice.publish_person = request.user.username
            notice.upload_person = request.user.username
            # 自动识别附件信息
            if request.FILES.get('attach_file'):
                attach_file = request.FILES.get('attach_file')
                notice.file_name = attach_file.name
                notice.file_size = attach_file.size
                import os
                notice.file_type = os.path.splitext(attach_file.name)[1].lower()
            notice.save()
            
            # 如果同时上传了多个文件，跳转到批量上传页面
            if request.FILES.getlist('files[]'):
                messages.success(request, '通知公告添加成功！请继续上传附件。')
                return redirect('eims_app:notice_batch_upload_page', pk=notice.id)
            else:
                messages.success(request, '通知公告添加成功！')
                # 重定向回添加页面，让 JavaScript 可以提取 ID 进行批量上传
                return redirect('eims_app:notice_add_with_id', pk=notice.id)
        else:
            # 显示具体的验证错误信息
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            if error_messages:
                messages.error(request, f'添加失败：{"; ".join(error_messages)}')
            else:
                messages.error(request, '添加失败，请检查输入内容是否合规！')
    else:
        form = NoticeForm()
        # 自动填充发布人为当前用户
        form.initial['publish_person'] = request.user.username
        # 如果有 pk，预填充通知数据
        if pk:
            notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
            # 可以在这里预填充表单字段

    back_url = '/notice/list/'
    context = {
        'form': form,
        'back_url': back_url,
        'active_menu': 'notice',
        'title': '添加通知公告'
    }
    return render(request, 'notice/notice_add.html', context)

# 编辑通知公告
@login_required
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
    original_status = notice.notice_status  # 记录原始状态
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            notice = form.save(commit=False)
            # 自动填充发布人为当前用户
            if not notice.publish_person:
                notice.publish_person = request.user.username
            notice.save()
            
            # 处理文件上传 - 必须在 notice.save() 之后
            if request.FILES.get('attach_file'):
                attach_file = request.FILES.get('attach_file')
                # 保存文件到文件系统
                notice.attach_file.save(attach_file.name, attach_file, save=True)
                # 更新文件信息
                notice.file_name = attach_file.name
                notice.file_size = attach_file.size
                import os
                notice.file_type = os.path.splitext(attach_file.name)[1].lower()
                notice.save()
            
            messages.success(request, '通知公告修改成功！')
            return redirect('eims_app:notice_detail', pk=pk)
        else:
            # 显示具体的验证错误信息
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            if error_messages:
                messages.error(request, f'修改失败：{"; ".join(error_messages)}')
            else:
                messages.error(request, '修改失败，请检查输入内容是否合规！')
    else:
        form = NoticeForm(instance=notice)
        # 如果发布人为空，自动填充当前用户
        if not notice.publish_person:
            form.initial['publish_person'] = request.user.username

    back_url = request.GET.get('back_url', f'/notice/{pk}/')
    context = {
        'form': form,
        'notice': notice,
        'back_url': back_url,
        'active_menu': 'notice',
        'title': '编辑通知公告'
    }
    return render(request, 'notice/notice_edit.html', context)

# 删除通知公告（软删除）
@login_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
    if request.method == 'POST':
        notice.is_deleted = True
        notice.save()
        messages.success(request, '通知公告已删除（软删除）！')
        return redirect('eims_app:notice_list')

    back_url = f'/notice/{pk}/'
    context = {
        'notice': notice,
        'back_url': back_url,
        'active_menu': 'notice'
    }
    return render(request, 'notice/notice_delete.html', context)

# 文件下载
@login_required
def notice_file_download(request, pk):
    """通知附件下载"""
    from django.http import FileResponse
    import os
    
    notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
    
    # 获取要下载的附件 ID
    attachment_id = request.GET.get('file')
    
    if not attachment_id:
        # 如果没有指定附件 ID，使用主附件
        if not notice.attach_file:
            messages.error(request, '该通知没有附件！')
            return redirect('eims_app:notice_detail', pk=pk)
        file_obj = notice.attach_file
        file_name = notice.file_name
    else:
        # 使用指定的附件
        from eims_app.models import NoticeAttachment
        attachment = get_object_or_404(NoticeAttachment, pk=attachment_id, is_deleted=False)
        file_obj = attachment.file
        file_name = attachment.file_name
    
    # 检查文件是否存在
    if os.path.exists(file_obj.path):
        response = FileResponse(open(file_obj.path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    else:
        messages.error(request, '文件不存在！')
        return redirect('eims_app:notice_detail', pk=pk)

# 文件预览（支持 PDF、图片、Word、Excel、PPT）
@login_required
def notice_file_preview(request, pk):
    """通知附件预览"""
    notice = get_object_or_404(Notice, pk=pk, is_deleted=False)
    
    # 获取要预览的附件 ID
    attachment_id = request.GET.get('file')
    
    if not attachment_id:
        # 如果没有指定附件 ID，检查是否有主附件
        if not notice.attach_file:
            messages.error(request, '该通知没有附件！')
            return redirect('eims_app:notice_detail', pk=pk)
        # 使用主附件
        attachment = None
        file_obj = notice.attach_file
        file_name = notice.file_name
        file_type = notice.file_type.lower() if notice.file_type else ''
    else:
        # 使用指定的附件
        from eims_app.models import NoticeAttachment
        attachment = get_object_or_404(NoticeAttachment, pk=attachment_id, is_deleted=False)
        file_obj = attachment.file
        file_name = attachment.file_name
        file_type = attachment.file_type.lower() if attachment.file_type else ''
    
    # 验证文件是否存在
    if not file_obj:
        messages.error(request, '文件不存在！')
        return redirect('eims_app:notice_detail', pk=pk)
    
    # 根据文件类型返回不同的预览方式
    context = {
        'notice': notice,
        'file_name': file_name,
        'file_type': file_type,
        'file_url': file_obj.url,
        'back_url': request.GET.get('back_url', f'/notice/{pk}/')
    }
    
    # 图片类型：直接显示
    if file_type in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        return render(request, 'notice/notice_preview_image.html', context)
    
    # PDF 类型：使用浏览器内置预览
    elif file_type == '.pdf':
        return render(request, 'notice/notice_preview_pdf.html', context)
    
    # Office 文档：使用微软 Office Online 预览（需要公网访问）
    elif file_type in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
        # 构建文件的完整 URL（用于 Office Online 预览）
        from django.conf import settings
        file_url = request.build_absolute_uri(file_obj.url)
        context['file_url'] = file_url
        
        # 检查是否是本地开发环境
        import socket
        try:
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            is_local = any(ip in file_url for ip in ['127.0.0.1', 'localhost'])
        except:
            is_local = '127.0.0.1' in file_url or 'localhost' in file_url
        
        context['is_local'] = is_local
        
        return render(request, 'notice/notice_preview_office.html', context)
    
    # 其他类型：提示下载
    else:
        messages.info(request, '该文件类型不支持在线预览，请下载后查看！')
        return redirect('eims_app:notice_file_download', pk=pk)