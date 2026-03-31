from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from eims_app.models import Department, DepartmentRole, ApprovalChain, Personnel
from eims_app.forms.form_department import DepartmentForm, DepartmentRoleForm, ApprovalChainForm
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test, login_required


def organization_navigation(request):
    """组织管理模块导航页面"""
    context = {
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "department/navigation.html", context)


def temp_welcome(request):
    """临时欢迎页面 - 用于测试路由是否工作"""
    return render(request, 'department/temp_welcome.html')


def is_superuser(user):
    return user.is_superuser


# ==================== 部门管理 ====================

@user_passes_test(is_superuser)
def department_list(request):
    """部门列表页面"""
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    department_type = request.GET.get('department_type', '')
    status = request.GET.get('status', '')
    
    # 基础查询集
    dept_list = Department.objects.filter(is_deleted=False).order_by('parent_department', 'order')
    
    # 筛选
    if search_key:
        dept_list = dept_list.filter(
            Q(department_name__icontains=search_key) |
            Q(department_code__icontains=search_key) |
            Q(manager_name__icontains=search_key)
        )
    
    if department_type:
        dept_list = dept_list.filter(department_type=department_type)
    
    if status:
        dept_list = dept_list.filter(status=status)
    
    # 分页
    paginator = Paginator(dept_list, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)
    
    context = {
        'page_obj': page_obj,
        'selected_keyword': search_key,
        'selected_department_type': department_type,
        'selected_status': status,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/list.html', context)


@user_passes_test(is_superuser)
def department_create(request):
    """创建部门"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save(commit=False)
            dept.save()
            messages.success(request, f'部门 "{dept.department_name}" 创建成功！')
            return redirect('eims_app:department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'title': '创建部门',
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/form.html', context)


@user_passes_test(is_superuser)
def department_edit(request, pk):
    """编辑部门"""
    dept = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'部门 "{dept.department_name}" 更新成功！')
            return redirect('eims_app:department_list')
    else:
        form = DepartmentForm(instance=dept)
    
    context = {
        'form': form,
        'dept': dept,
        'title': '编辑部门',
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/form.html', context)


@user_passes_test(is_superuser)
def department_delete(request, pk):
    """删除部门（软删除）"""
    dept = get_object_or_404(Department, pk=pk)
    
    # 检查是否有下属人员
    personnel_count = Personnel.objects.filter(department=dept.department_name, is_deleted=False).count()
    if personnel_count > 0:
        messages.error(request, f'该部门下还有 {personnel_count} 名人员，无法删除！')
        return redirect('eims_app:department_list')
    
    try:
        dept.is_deleted = True
        dept.save(update_fields=['is_deleted'])
        messages.success(request, f'部门 "{dept.department_name}" 已删除。')
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')
    
    return redirect('eims_app:department_list')


@user_passes_test(is_superuser)
def department_detail(request, pk):
    """部门详情"""
    dept = get_object_or_404(Department, pk=pk)
    
    # 获取部门成员
    members = Personnel.objects.filter(department=dept.department_name, is_deleted=False)
    
    # 获取部门角色配置
    roles = DepartmentRole.objects.filter(department=dept, is_deleted=False)
    
    context = {
        'dept': dept,
        'members': members,
        'roles': roles,
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/detail.html', context)


# ==================== 部门角色管理 ====================

@user_passes_test(is_superuser)
def department_role_list(request):
    """部门角色列表"""
    
    search_key = request.GET.get('keyword', '')
    department_id = request.GET.get('department', '')
    role_type = request.GET.get('role_type', '')
    
    role_list = DepartmentRole.objects.filter(is_deleted=False).select_related('department', 'user').order_by('department', 'role_type')
    
    if search_key:
        role_list = role_list.filter(
            Q(role_name__icontains=search_key) |
            Q(user__username__icontains=search_key)
        )
    
    if department_id:
        role_list = role_list.filter(department_id=department_id)
    
    if role_type:
        role_list = role_list.filter(role_type=role_type)
    
    paginator = Paginator(role_list, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)
    
    context = {
        'page_obj': page_obj,
        'selected_keyword': search_key,
        'selected_department': department_id,
        'selected_role_type': role_type,
        'all_departments': Department.objects.filter(is_deleted=False),
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/role_list.html', context)


@user_passes_test(is_superuser)
def department_role_create(request):
    """创建部门角色"""
    if request.method == 'POST':
        form = DepartmentRoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.save()
            messages.success(request, f'角色 "{role.role_name}" 配置成功！')
            return redirect('eims_app:department_role_list')
    else:
        form = DepartmentRoleForm()
    
    context = {
        'form': form,
        'title': '配置部门角色',
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/role_form.html', context)


@user_passes_test(is_superuser)
def department_role_edit(request, pk):
    """编辑部门角色"""
    role = get_object_or_404(DepartmentRole, pk=pk)
    
    if request.method == 'POST':
        # 编辑模式下，排除用户字段（不允许修改用户）
        form = DepartmentRoleForm(request.POST, instance=role)
        if form.is_valid():
            # 保存时保持原用户不变
            role = form.save(commit=False)
            role.user = role.user  # 保持原用户
            role.save()
            messages.success(request, f'角色 "{role.role_name}" 更新成功！')
            # 返回列表页
            return redirect('eims_app:department_role_list')
        else:
            # 表单验证失败，打印错误信息
            print("表单验证失败：", form.errors)
            messages.error(request, f'保存失败：{form.errors}')
    else:
        form = DepartmentRoleForm(instance=role)
    
    context = {
        'form': form,
        'role': role,
        'title': '编辑部门角色',
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/role_form.html', context)


@user_passes_test(is_superuser)
def department_role_delete(request, pk):
    """删除部门角色"""
    role = get_object_or_404(DepartmentRole, pk=pk)
    
    try:
        role.is_deleted = True
        role.save(update_fields=['is_deleted'])
        messages.success(request, f'角色配置已删除。')
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')
    
    return redirect('eims_app:department_role_list')


@login_required
@user_passes_test(is_superuser)
def add_role_type(request):
    """动态添加新的角色类型（AJAX）"""
    import json
    from django.http import JsonResponse
    from django.conf import settings
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            name = data.get('name', '').strip()
            
            # 验证输入
            if not code or not name:
                return JsonResponse({'success': False, 'error': '角色类型代码和名称不能为空'})
            
            # 验证代码格式
            import re
            if not re.match(r'^[a-z_]+$', code):
                return JsonResponse({'success': False, 'error': '角色类型代码只能使用小写字母和下划线'})
            
            # 检查是否已存在
            existing_choices = [choice[0] for choice in DepartmentRole.ROLE_TYPE_CHOICES]
            if code in existing_choices:
                return JsonResponse({'success': False, 'error': f'角色类型 "{code}" 已存在'})
            
            # 动态添加到 CHOICES
            # 注意：这种修改只在运行时有效，重启后会恢复
            # 如果需要永久保存，需要修改模型文件或使用数据库存储
            DepartmentRole.ROLE_TYPE_CHOICES.append((code, name))
            
            # 可选：保存到数据库配置表（如果需要持久化）
            # 这里可以使用缓存或配置文件来存储
            
            return JsonResponse({'success': True, 'message': '添加成功'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': '无效的请求数据'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'服务器错误：{str(e)}'})
    
    return JsonResponse({'success': False, 'error': '请求方法错误'})


# ==================== 审批链管理 ====================

@user_passes_test(is_superuser)
def approval_chain_list(request):
    """审批链列表"""
    
    business_type = request.GET.get('business_type', '')
    is_active = request.GET.get('is_active', '')
    
    chain_list = ApprovalChain.objects.filter(is_deleted=False).order_by('business_type', 'name')
    
    if business_type:
        chain_list = chain_list.filter(business_type=business_type)
    
    if is_active != '':
        chain_list = chain_list.filter(is_active=(is_active == 'true'))
    
    paginator = Paginator(chain_list, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)
    
    context = {
        'page_obj': page_obj,
        'selected_business_type': business_type,
        'selected_is_active': is_active,
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/approval_chain_list.html', context)


@user_passes_test(is_superuser)
def approval_chain_create(request):
    """创建审批链"""
    if request.method == 'POST':
        form = ApprovalChainForm(request.POST)
        if form.is_valid():
            chain = form.save(commit=False)
            chain.save()
            form.save_m2m()  # 保存多对多关系
            messages.success(request, f'审批链 "{chain.name}" 创建成功！')
            return redirect('eims_app:approval_chain_list')
    else:
        form = ApprovalChainForm()
    
    context = {
        'form': form,
        'title': '创建审批链',
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/approval_chain_form.html', context)


@user_passes_test(is_superuser)
def approval_chain_edit(request, pk):
    """编辑审批链"""
    chain = get_object_or_404(ApprovalChain, pk=pk)
    
    if request.method == 'POST':
        form = ApprovalChainForm(request.POST, instance=chain)
        if form.is_valid():
            chain = form.save()
            messages.success(request, f'审批链 "{chain.name}" 更新成功！')
            return redirect('eims_app:approval_chain_list')
    else:
        form = ApprovalChainForm(instance=chain)
    
    context = {
        'form': form,
        'chain': chain,
        'title': '编辑审批链',
        'home_url': reverse('eims_app:eims_index'),
    }
    return render(request, 'department/approval_chain_form.html', context)


@user_passes_test(is_superuser)
def approval_chain_delete(request, pk):
    """删除审批链"""
    chain = get_object_or_404(ApprovalChain, pk=pk)
    
    try:
        chain.is_deleted = True
        chain.save(update_fields=['is_deleted'])
        messages.success(request, f'审批链已删除。')
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')
    
    return redirect('eims_app:approval_chain_list')
