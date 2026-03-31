from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse
import os
from eims_app.models import FileManage
from eims_app.forms import FileForm
from django.conf import settings
import mimetypes

# 文件列表（匹配导入的 file_list）
@login_required
def file_list(request):
    search_key = request.GET.get('search', '')
    file_category = request.GET.get('file_category', '')
    
    # 基础查询：过滤已删除文件，关联 FileManage 模型
    files = FileManage.objects.filter(is_deleted=False)
    
    # 搜索过滤（模糊匹配文件名、内容摘要）
    if search_key:
        files = files.filter(
            Q(file_name__icontains=search_key) |
            Q(content_summary__icontains=search_key) |
            Q(file_number__icontains=search_key)
        )
    
    # 文件类别过滤
    if file_category:
        files = files.filter(file_category=file_category)
    
    # 按发布时间倒序排列
    files = files.order_by('-publish_time')
    
    # 构造模板上下文
    context = {
        'files': files,
        'search_key': search_key,
        'file_category': file_category,
    }
    return render(request, 'file_manage/file_manage_list.html', context)

# 文件详情（匹配导入的 file_detail）
@login_required
def file_detail(request, file_id):
    # 获取单个文件信息，不存在返回 404
    file_obj = get_object_or_404(FileManage, id=file_id, is_deleted=False)
    return render(request, 'file_manage/file_manage_detail.html', {'file': file_obj})

# 文件添加（匹配导入的 file_add，核心解决当前报错）
@login_required
def file_add(request):
    if request.method == 'POST':
        # 处理文件上传，需用 request.FILES 接收文件字段
        form = FileForm(request.POST, request.FILES)
        form.context = {'request': request}  # 传递 request 上下文
        if form.is_valid():
            print(f"Form is valid! Cleaned data: {form.cleaned_data}")
            file_obj = form.save(commit=False)
            # 手动设置上传人
            if request.user.is_authenticated:
                file_obj.uploader = request.user.username
            else:
                file_obj.uploader = '系统'
            print(f"Before save - File name: {file_obj.file_name}, Category: {file_obj.file_category}")
            file_obj.save()
            print(f"After save - File ID: {file_obj.id}")
            messages.success(request, '文件上传成功！')
            return redirect('eims_app:file_manage_list')
        else:
            # 打印验证错误
            print(f"Form errors: {form.errors}")
            print(f"Form is NOT valid. Files in request: {'file_path' in request.FILES}")
        messages.error(request, '文件上传失败，请检查文件格式和填写信息！')
    else:
        form = FileForm()
    return render(request, 'file_manage/file_manage_add.html', {'form': form, 'title': '上传文件'})

# 文件编辑（匹配导入的 file_edit）
@login_required
def file_edit(request, file_id):
    file_obj = get_object_or_404(FileManage, id=file_id, is_deleted=False)
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES, instance=file_obj)
        form.context = {'request': request}  # 传递 request 上下文
        if form.is_valid():
            form.save()
            messages.success(request, '文件信息修改成功！')
            return redirect('eims_app:file_manage_detail', file_id=file_obj.id)
        messages.error(request, '修改失败，请检查信息！')
    else:
        form = FileForm(instance=file_obj)
        # 为只读字段设置初始值
        if file_obj.file_format:
            form.fields['file_format'].initial = file_obj.file_format
    return render(request, 'file_manage/file_manage_edit.html', {'form': form, 'title': '编辑文件', 'file': file_obj})

# 文件删除（匹配导入的 file_delete）
@login_required
def file_delete(request, file_id):
    file_obj = get_object_or_404(FileManage, id=file_id, is_deleted=False)
    # 软删除：标记is_deleted=True，不真正删除文件
    file_obj.is_deleted = True
    file_obj.save()
    messages.success(request, '文件已删除！')
    return redirect('eims_app:file_manage_list')

# 文件下载（匹配导入的 file_download）
@login_required
def file_download(request, file_id):
    file_obj = get_object_or_404(FileManage, id=file_id, is_deleted=False)
    # 获取文件实际路径（需模型有 file_path 字段，存储文件路径）
    file_path = os.path.join(settings.MEDIA_ROOT, str(file_obj.file_path))
    
    # 验证文件是否存在
    if not os.path.exists(file_path):
        messages.error(request, '文件不存在或已被删除！')
        return redirect('eims_app:file_manage_list')
    
    # 读取文件并返回下载响应
    file = open(file_path, 'rb')
    response = FileResponse(file)
    # 设置响应头，指定下载文件名
    response['Content-Disposition'] = f'attachment; filename="{file_obj.file_name}"'
    return response

# 文件预览
@login_required
def file_preview(request, file_id):
    """文件在线预览"""
    file_obj = get_object_or_404(FileManage, id=file_id, is_deleted=False)
    
    # 获取文件实际路径
    file_path = os.path.join(settings.MEDIA_ROOT, str(file_obj.file_path))
    
    # 验证文件是否存在
    if not os.path.exists(file_path):
        messages.error(request, '文件不存在或已被删除！')
        return redirect('eims_app:file_manage_list')
    
    # 获取文件类型
    file_type = file_obj.file_type.lower() if file_obj.file_type else ''
    
    # 构造预览上下文
    context = {
        'file': file_obj,
        'file_type': file_type,
        'file_url': file_obj.file_path.url
    }
    
    # 根据文件类型返回不同的预览方式
    if file_type in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        # 图片类型：直接显示
        return render(request, 'file_manage/file_preview_image.html', context)
    elif file_type in ['.pdf']:
        # PDF：使用浏览器内置预览
        return render(request, 'file_manage/file_preview_pdf.html', context)
    elif file_type in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
        # Office 文档：使用 Office Online 预览
        return render(request, 'file_manage/file_preview_office.html', context)
    else:
        # 其他类型：提示不支持预览
        messages.info(request, '该文件类型不支持在线预览，请下载查看。')
        return redirect('eims_app:file_manage_detail', file_id=file_id)