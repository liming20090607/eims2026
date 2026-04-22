import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from eims_app.models import PersonnelCertificate, PersonnelAllocation, Personnel
from eims_app.utils.tenant_utils import filter_queryset_by_tenant
from eims_app.models.model_project_detail import ProjectDetail  # 改用 ProjectDetail
from eims_app.forms.form_personnel_detail import PersonnelCertificateForm, PersonnelAllocationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

def is_superuser(user):
    return user.is_superuser

def has_personnel_permission(user):
    """检查用户是否具有人员管理权限"""
    if user.is_superuser:
        return True
    return user.has_perm('eims_app.view_personnel') or user.has_perm('eims_app.change_personnel')

# ==================== 人员证书管理 ====================

@login_required
@user_passes_test(has_personnel_permission)
def certificate_list(request):
    """人员证书列表页面"""
    
    # 如果是 /root/ 路径且没有选择公司，重定向到公司选择页面
    if hasattr(request, 'current_system') and request.current_system == 'root':
        if not hasattr(request, 'tenant') or not request.tenant:
            from django.contrib import messages
            messages.warning(request, '请先选择要查看的公司')
            return redirect('eims_app:tenant_select')
    
    # 1. 获取筛选参数
    search_key = request.GET.get('keyword', '')
    certificate_type = request.GET.get('certificate_type', '')
    personnel_code = request.GET.get('personnel_code', '')
    
    # 2. 基础查询集
    certificate_list = PersonnelCertificate.objects.filter(is_deleted=False).order_by('-create_time')
    
    # 应用租户过滤
    certificate_list = filter_queryset_by_tenant(certificate_list, request)
    
    # 3. 多条件筛选
    if search_key:
        certificate_list = certificate_list.filter(
            Q(certificate_name__icontains=search_key) |
            Q(certificate_code__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(issuing_authority__icontains=search_key)
        ).distinct()
    
    if certificate_type:
        certificate_list = certificate_list.filter(certificate_type=certificate_type)
    
    if personnel_code:
        certificate_list = certificate_list.filter(personnel_code=personnel_code)
    
    # 4. 预获取人员信息（按租户过滤）
    personnel_filter = {'is_deleted': False}
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
    
    personnel_info = {}
    for p in Personnel.objects.filter(**personnel_filter):
        personnel_info[p.personnel_code] = p
    
    # 为证书对象附加人员姓名
    for cert in certificate_list:
        if cert.personnel_code in personnel_info:
            cert.personnel_name = personnel_info[cert.personnel_code].name
        else:
            cert.personnel_name = ''
    
    # 5. 分页处理
    paginator = Paginator(certificate_list, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        page_obj = paginator.page(1)
    
    # 6. 统计信息
    total_certificates = PersonnelCertificate.objects.filter(is_deleted=False).count()
    
    context = {
        "page_obj": page_obj,
        "selected_keyword": search_key,
        "selected_certificate_type": certificate_type,
        "selected_personnel_code": personnel_code,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
        'total_certificates': total_certificates,
    }
    
    # 获取人员列表，按租户过滤
    personnel_filter = {'is_deleted': False}
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
    
    context['all_personnel'] = Personnel.objects.filter(**personnel_filter).order_by('personnel_code')
    
    return render(request, "personnel/certificate_list.html", context)


@login_required
@user_passes_test(has_personnel_permission)
def certificate_create(request):
    """创建人员证书"""
    if request.method == 'POST':
        form = PersonnelCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.operator = request.user.username if request.user.is_authenticated else ''
            certificate.save()
            messages.success(request, f'证书 "{certificate.certificate_name}" 创建成功！')
            return redirect('eims_app:certificate_list')
        else:
            messages.error(request, '请修正表单中的错误。')
    else:
        form = PersonnelCertificateForm()
    
    context = {
        'form': form,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/certificate_form.html", context)


@login_required
@user_passes_test(has_personnel_permission)
def certificate_edit(request, pk):
    """编辑人员证书"""
    certificate = get_object_or_404(PersonnelCertificate, pk=pk)
    
    if request.method == 'POST':
        form = PersonnelCertificateForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.operator = request.user.username if request.user.is_authenticated else ''
            certificate.save()
            messages.success(request, f'证书 "{certificate.certificate_name}" 更新成功！')
            return redirect('eims_app:certificate_list')
        else:
            messages.error(request, '请修正表单中的错误。')
    else:
        form = PersonnelCertificateForm(instance=certificate)
    
    context = {
        'form': form,
        'certificate': certificate,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/certificate_form.html", context)


@login_required
@user_passes_test(has_personnel_permission)
def certificate_delete(request, pk):
    """删除人员证书（软删除）"""
    certificate = get_object_or_404(PersonnelCertificate, pk=pk)
    
    try:
        certificate.is_deleted = True
        certificate.save(update_fields=['is_deleted'])
        messages.success(request, f'证书 "{certificate.certificate_name}" 已删除。')
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')
    
    return redirect('eims_app:certificate_list')


@login_required
@user_passes_test(has_personnel_permission)
def certificate_detail(request, pk):
    """人员证书详情"""
    certificate = get_object_or_404(PersonnelCertificate, pk=pk)
    
    context = {
        'certificate': certificate,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/certificate_detail.html", context)


# ==================== 人员分配管理 ====================

@login_required
@user_passes_test(has_personnel_permission)
def allocation_list(request):
    """人员分配列表页面"""
    
    # 如果是 /root/ 路径且没有选择公司，重定向到公司选择页面
    if hasattr(request, 'current_system') and request.current_system == 'root':
        if not hasattr(request, 'tenant') or not request.tenant:
            from django.contrib import messages
            messages.warning(request, '请先选择要查看的公司')
            return redirect('eims_app:tenant_select')
    
    # 1. 获取筛选参数
    search_key = request.GET.get('keyword', '')
    allocation_status = request.GET.get('allocation_status', '')
    personnel_code = request.GET.get('personnel_code', '')
    to_project_code = request.GET.get('to_project_code', '')
    
    # 2. 基础查询集
    allocation_list = PersonnelAllocation.objects.filter(is_deleted=False).order_by('-allocation_date')
    
    # 应用租户过滤
    allocation_list = filter_queryset_by_tenant(allocation_list, request)
    
    # 3. 多条件筛选
    if search_key:
        allocation_list = allocation_list.filter(
            Q(allocation_code__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(allocation_position__icontains=search_key) |
            Q(to_project_code__icontains=search_key)
        ).distinct()
    
    if allocation_status:
        allocation_list = allocation_list.filter(allocation_status=allocation_status)
    
    if personnel_code:
        allocation_list = allocation_list.filter(personnel_code=personnel_code)
    
    if to_project_code:
        allocation_list = allocation_list.filter(to_project_code=to_project_code)
    
    # 4. 预获取人员和项目信息（按租户过滤）
    # 注意：ProjectDetail模型没有is_deleted字段
    personnel_filter = {'is_deleted': False}
    project_filter = {}
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
        project_filter['tenant_id'] = request.tenant.id
    
    personnel_info = {}
    for p in Personnel.objects.filter(**personnel_filter):
        personnel_info[p.personnel_code] = p
    
    project_info = {}
    for p in ProjectDetail.objects.filter(**project_filter):
        project_info[p.project_code] = p
    
    # 为分配对象附加名称
    for alloc in allocation_list:
        if alloc.personnel_code in personnel_info:
            alloc.personnel_name = personnel_info[alloc.personnel_code].name
        else:
            alloc.personnel_name = ''
        
        if alloc.to_project_code in project_info:
            alloc.to_project_name = project_info[alloc.to_project_code].project_name if project_info[alloc.to_project_code].project_name else ''
        else:
            alloc.to_project_name = ''
        
        if alloc.from_project_code and alloc.from_project_code in project_info:
            proj = project_info[alloc.from_project_code]
            alloc.from_project_name = proj.project_name if proj.project_name else ''
        else:
            alloc.from_project_name = '-'
    
    # 5. 分页处理
    paginator = Paginator(allocation_list, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        page_obj = paginator.page(1)
    
    # 6. 统计信息
    total_allocations = PersonnelAllocation.objects.filter(is_deleted=False).count()
    
    context = {
        "page_obj": page_obj,
        "selected_keyword": search_key,
        "selected_allocation_status": allocation_status,
        "selected_personnel_code": personnel_code,
        "selected_to_project_code": to_project_code,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
        'total_allocations': total_allocations,
    }
    
    # 获取人员列表，按租户过滤
    personnel_filter = {'is_deleted': False}
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
    
    context['all_personnel'] = Personnel.objects.filter(**personnel_filter).order_by('personnel_code')
    
    # 获取项目列表，按租户过滤
    proj_filter = {}
    if hasattr(request, 'tenant') and request.tenant:
        proj_filter['tenant_id'] = request.tenant.id
    
    context['all_projects'] = ProjectDetail.objects.filter(**proj_filter).order_by('project_code')
    
    return render(request, "personnel/allocation_list.html", context)


@login_required
@user_passes_test(has_personnel_permission)
def allocation_create(request):
    """创建人员分配"""
    if request.method == 'POST':
        form = PersonnelAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.operator = request.user.username if request.user.is_authenticated else ''
            allocation.save()
            messages.success(request, f'人员 "{allocation.personnel_code}" 分配成功！')
            return redirect('eims_app:allocation_list')
        else:
            messages.error(request, '请修正表单中的错误。')
    else:
        form = PersonnelAllocationForm()
    
    context = {
        'form': form,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/allocation_form.html", context)


@login_required
@user_passes_test(has_personnel_permission)
def allocation_edit(request, pk):
    """编辑人员分配"""
    allocation = get_object_or_404(PersonnelAllocation, pk=pk)
    
    if request.method == 'POST':
        form = PersonnelAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.operator = request.user.username if request.user.is_authenticated else ''
            allocation.save()
            messages.success(request, f'分配记录 "{allocation.allocation_code}" 更新成功！')
            return redirect('eims_app:allocation_list')
        else:
            messages.error(request, '请修正表单中的错误。')
    else:
        form = PersonnelAllocationForm(instance=allocation)
    
    context = {
        'form': form,
        'allocation': allocation,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/allocation_form.html", context)


@login_required
@user_passes_test(has_personnel_permission)
def allocation_delete(request, pk):
    """删除人员分配（软删除）"""
    allocation = get_object_or_404(PersonnelAllocation, pk=pk)
    
    try:
        allocation.is_deleted = True
        allocation.save(update_fields=['is_deleted'])
        messages.success(request, f'分配记录 "{allocation.allocation_code}" 已删除。')
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')
    
    return redirect('eims_app:allocation_list')


@login_required
@user_passes_test(has_personnel_permission)
def allocation_detail(request, pk):
    """人员分配详情"""
    allocation = get_object_or_404(PersonnelAllocation, pk=pk)
    
    context = {
        'allocation': allocation,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/allocation_detail.html", context)
