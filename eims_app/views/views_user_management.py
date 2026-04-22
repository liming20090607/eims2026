import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import Group as AuthGroup
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from eims_app.models import Employee, Tenant, UserTenantRelation
from eims_app.forms.form_user_management import BatchUserCreateForm, PasswordResetForm

logger = logging.getLogger(__name__)
User = get_user_model()

def is_superuser(user):
    """检查是否为超级管理员"""
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def user_management(request):
    """用户账号管理页面"""
    
    # 获取搜索关键词
    search_keyword = request.GET.get('search', '').strip()
    
    # 获取所有员工（基础查询集，按租户过滤）
    if hasattr(request, 'tenant') and request.tenant:
        employees = Employee.objects.filter(is_deleted=False, tenant_id=request.tenant.id)
    else:
        employees = Employee.objects.filter(is_deleted=False)
    
    # 如果有搜索关键词，进行模糊搜索
    if search_keyword:
        # 搜索员工信息（姓名、职位、公司）
        employees = employees.filter(
            Q(name__icontains=search_keyword) |
            Q(admin_position__icontains=search_keyword) |
            Q(tenant__name__icontains=search_keyword)
        )
    
    employees = employees.order_by('personnel_code')
    
    # 获取已创建账号的员工（通过手机号或姓名关联 User）
    existing_users = User.objects.all()
    
    # 为员工匹配账号状态
    employee_account_status = []
    for emp in employees:
        # 尝试通过手机号或姓名查找对应的用户
        user = None
        # 优先匹配手机号
        if emp.mobile:
            user = User.objects.filter(username=emp.mobile).first()
        # 如果没找到，尝试匹配姓名
        if not user:
            user = User.objects.filter(username=emp.name).first()
        
        # 获取用户组信息
        user_groups = []
        user_group_ids = []
        user_tenant = None
        user_tenant_relations = []
        has_password = False  # 密码状态
        if user:
            user_groups = list(user.groups.all().values_list('name', flat=True))
            user_group_ids = list(user.groups.all().values_list('id', flat=True))
            
            # 检查用户是否设置了密码（Django 存储的是哈希值，检查是否有值）
            has_password = bool(user.password and user.password != '')
            
            # 获取用户所属公司关联（支持多公司）
            try:
                relations = UserTenantRelation.objects.filter(user=user).select_related('tenant')
                user_tenant_relations = list(relations)
                # 兼容旧字段：取主公司或第一个公司
                primary_rel = next((r for r in relations if r.is_primary), None)
                user_tenant = primary_rel.tenant if primary_rel else (relations[0].tenant if relations else None)
            except:
                # 如果新表查询失败，尝试兼容旧字段
                try:
                    user_tenant = user.profile.tenant
                except:
                    pass
            
            # 如果有关键词，也搜索用户名和用户组
            if search_keyword:
                # 检查用户名是否匹配
                username_match = search_keyword.lower() in user.username.lower()
                # 检查用户组是否匹配
                group_match = any(search_keyword.lower() in group.lower() for group in user_groups)
                
                # 如果用户名和用户组都不匹配，且员工信息也不匹配，则跳过
                if not username_match and not group_match:
                    # 检查是否已经在员工查询中匹配（通过 Q 查询）
                    emp_match = (
                        search_keyword.lower() in emp.name.lower() or
                        (emp.admin_position and search_keyword.lower() in emp.admin_position.lower()) or
                        (emp.tenant and search_keyword.lower() in emp.tenant.name.lower())
                    )
                    if not emp_match:
                        continue
        
        employee_account_status.append({
            'employee': emp,
            'has_account': user is not None,
            'user': user,
            'user_groups': user_groups,
            'user_group_ids': user_group_ids,
            'user_tenant': user_tenant,
            'user_tenant_relations': user_tenant_relations,
            'has_password': has_password,  # 添加密码状态
        })
    
    # 分页处理 - 每页显示25条记录
    paginator = Paginator(employee_account_status, 25)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # 如果页码不是整数，显示第一页
        page_obj = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，显示最后一页
        page_obj = paginator.page(paginator.num_pages)
    
    # 处理批量创建
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'batch_create':
            # 批量创建账号
            selected_ids = request.POST.getlist('selected_employees')
            default_password = request.POST.get('default_password', 'sc123456#')
            
            created_count = 0
            failed_count = 0
            skipped_count = 0
            
            for emp_id in selected_ids:
                try:
                    # 按租户过滤，防止跨租户操作
                    if hasattr(request, 'tenant') and request.tenant:
                        emp = Employee.objects.get(id=emp_id, tenant_id=request.tenant.id)
                    else:
                        emp = Employee.objects.get(id=emp_id)
                    
                    # 优先使用手机号作为用户名
                    username = emp.mobile if emp.mobile else emp.name
                    
                    # 检查是否已存在
                    if User.objects.filter(username=username).exists():
                        skipped_count += 1
                        continue
                    
                    # 创建用户
                    user = User.objects.create_user(
                        username=username,
                        password=default_password,
                        first_name=emp.name,
                        email=emp.email if hasattr(emp, 'email') and emp.email else '',
                    )
                    
                    # 保存额外信息
                    user.save()
                    created_count += 1
                    
                    logger.info(f"为用户 {emp.name} ({username}) 创建账号成功")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"创建用户 {emp.name} 失败：{str(e)}")
            
            messages.success(
                request,
                f"批量创建完成！成功：{created_count}，跳过：{skipped_count}，失败：{failed_count}"
            )
            return redirect('eims_app:user_management')
        
        elif action == 'reset_password':
            # 重置密码
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                user_id = form.cleaned_data['user_id']
                new_password = form.cleaned_data['new_password']
                
                try:
                    user = User.objects.get(id=user_id)
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, f"用户 {user.username} 密码重置成功")
                except Exception as e:
                    messages.error(request, f"密码重置失败：{str(e)}")
            else:
                messages.error(request, "密码格式不正确")
            
            return redirect('eims_app:user_management')
        
        elif action == 'batch_update_groups':
            # 批量更新用户组
            selected_ids_str = request.POST.get('selected_ids', '')
            group_ids_str = request.POST.get('group_ids', '')
            
            # 解析逗号分隔的ID字符串
            selected_ids = [int(x) for x in selected_ids_str.split(',') if x.strip().isdigit()] if selected_ids_str else []
            group_ids = [int(x) for x in group_ids_str.split(',') if x.strip().isdigit()] if group_ids_str else []
            
            if not selected_ids or not group_ids:
                messages.error(request, '请选择员工和用户组！')
                return redirect('eims_app:user_management')
            
            success_count = 0
            failed_count = 0
            
            # 获取所有选中的用户组对象
            groups = AuthGroup.objects.filter(id__in=group_ids)
            
            for emp_id in selected_ids:
                try:
                    # 按租户过滤，防止跨租户操作
                    if hasattr(request, 'tenant') and request.tenant:
                        emp = Employee.objects.get(id=emp_id, tenant_id=request.tenant.id)
                    else:
                        emp = Employee.objects.get(id=emp_id)
                    
                    # 获取或创建该员工对应的用户
                    user = None
                    if emp.mobile:
                        user = User.objects.filter(username=emp.mobile).first()
                    if not user:
                        user = User.objects.filter(username=emp.name).first()
                    
                    if not user:
                        failed_count += 1
                        continue
                    
                    # 清除用户现有的所有用户组
                    user.groups.clear()
                    
                    # 添加新的用户组
                    user.groups.add(*groups)
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f'批量分组失败 {emp_id}: {str(e)}')
            
            messages.success(
                request,
                f'批量分组完成！成功：{success_count}，失败：{failed_count}'
            )
            return redirect('eims_app:user_management')
        
        elif action == 'batch_assign_tenant':
            # 批量分配公司
            selected_ids = request.POST.getlist('selected_employees')
            tenant_ids = request.POST.getlist('tenant_ids')
            primary_tenant_id = request.POST.get('primary_tenant_id')
            
            if not selected_ids or not tenant_ids:
                messages.error(request, '请选择员工和公司！')
                return redirect('eims_app:user_management')
            
            if not primary_tenant_id or primary_tenant_id not in tenant_ids:
                messages.error(request, '请选择一个主公司（必须在已选公司中）！')
                return redirect('eims_app:user_management')
            
            success_count = 0
            failed_count = 0
            
            for emp_id in selected_ids:
                try:
                    # 按租户过滤，防止跨租户操作
                    if hasattr(request, 'tenant') and request.tenant:
                        emp = Employee.objects.get(id=emp_id, tenant_id=request.tenant.id)
                    else:
                        emp = Employee.objects.get(id=emp_id)
                    
                    # 获取或创建该员工对应的用户
                    user = None
                    if emp.mobile:
                        user = User.objects.filter(username=emp.mobile).first()
                    if not user:
                        user = User.objects.filter(username=emp.name).first()
                    
                    if not user:
                        failed_count += 1
                        continue
                    
                    # 先删除该用户现有的公司关联
                    UserTenantRelation.objects.filter(user=user).delete()
                    
                    # 创建新的公司关联
                    for tid in tenant_ids:
                        is_primary = (tid == primary_tenant_id)
                        UserTenantRelation.objects.create(
                            user=user,
                            tenant_id=tid,
                            is_primary=is_primary,
                            remark='通过用户管理分配'
                        )
                    
                    # 同时更新 UserProfile.tenant 和 Employee.tenant 为主公司
                    try:
                        profile = user.profile
                        profile.tenant_id = primary_tenant_id
                        profile.save(update_fields=['tenant'])
                    except:
                        pass
                    
                    # 更新员工记录的主公司
                    try:
                        emp.tenant_id = primary_tenant_id
                        emp.save(update_fields=['tenant'])
                    except:
                        pass
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f'分配公司失败 {emp_id}: {str(e)}')
            
            messages.success(
                request,
                f'批量分配公司完成！成功：{success_count}，失败：{failed_count}'
            )
            return redirect('eims_app:user_management')
        
        elif action == 'update_user_groups':
            # 更新用户组
            user_id = request.POST.get('user_id')
            group_ids = request.POST.getlist('group_ids')
            
            try:
                user = User.objects.get(id=user_id)
                
                # 清空现有组
                user.groups.clear()
                
                # 添加新组
                if group_ids:
                    groups = AuthGroup.objects.filter(id__in=group_ids)
                    user.groups.add(*groups)
                
                user.save()
                messages.success(request, f"用户 {user.username} 的用户组更新成功")
            except Exception as e:
                messages.error(request, f"用户组更新失败：{str(e)}")
            
            return redirect('eims_app:user_management')
    
    # GET 请求，显示页面
    form = BatchUserCreateForm()
    password_reset_form = PasswordResetForm()
    
    # 获取所有用户组（用于下拉选择）
    all_groups = AuthGroup.objects.all().order_by('name')
    
    # 获取所有启用的租户公司（用于分配公司下拉列表）
    tenants = Tenant.objects.filter(is_active=True).order_by('code')
    
    # 为员工匹配账号状态
    employee_account_status = []
    for emp in employees:
        # 尝试通过手机号或姓名查找对应的用户
        user = None
        # 优先匹配手机号
        if emp.mobile:
            user = User.objects.filter(username=emp.mobile).first()
        # 如果没找到，尝试匹配姓名
        if not user:
            user = User.objects.filter(username=emp.name).first()
        
        # 获取用户组信息
        user_groups = []
        user_group_ids = []
        user_tenant = None
        user_tenant_relations = []
        has_password = False  # 密码状态
        if user:
            user_groups = list(user.groups.all().values_list('name', flat=True))
            user_group_ids = list(user.groups.all().values_list('id', flat=True))
            
            # 检查用户是否设置了密码（Django 存储的是哈希值，检查是否有值）
            has_password = bool(user.password and user.password != '')
            
            # 获取用户所属公司关联（支持多公司）
            try:
                relations = UserTenantRelation.objects.filter(user=user).select_related('tenant')
                user_tenant_relations = list(relations)
                # 兼容旧字段：取主公司或第一个公司
                primary_rel = next((r for r in relations if r.is_primary), None)
                user_tenant = primary_rel.tenant if primary_rel else (relations[0].tenant if relations else None)
            except:
                # 如果新表查询失败，尝试兼容旧字段
                try:
                    user_tenant = user.profile.tenant
                except:
                    pass
            
            # 如果有关键词，也搜索用户名和用户组
            if search_keyword:
                # 检查用户名是否匹配
                username_match = search_keyword.lower() in user.username.lower()
                # 检查用户组是否匹配
                group_match = any(search_keyword.lower() in group.lower() for group in user_groups)
                
                # 如果用户名和用户组都不匹配，且员工信息也不匹配，则跳过
                if not username_match and not group_match:
                    # 检查是否已经在员工查询中匹配（通过 Q 查询）
                    emp_match = (
                        search_keyword.lower() in emp.name.lower() or
                        (emp.admin_position and search_keyword.lower() in emp.admin_position.lower()) or
                        (emp.tenant and search_keyword.lower() in emp.tenant.name.lower())
                    )
                    if not emp_match:
                        continue
        
        employee_account_status.append({
            'employee': emp,
            'has_account': user is not None,
            'user': user,
            'user_groups': user_groups,
            'user_group_ids': user_group_ids,
            'user_tenant': user_tenant,
            'user_tenant_relations': user_tenant_relations,
            'has_password': has_password,  # 添加密码状态
        })
    
    # 分页处理 - 每页显示25条记录
    paginator = Paginator(employee_account_status, 25)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # 如果页码不是整数，显示第一页
        page_obj = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，显示最后一页
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'employee_account_status': employee_account_status,
        'form': form,
        'password_reset_form': password_reset_form,
        'all_groups': all_groups,
        'tenants': tenants,
        'total_employees': employees.count(),
        'has_accounts': sum(1 for e in employee_account_status if e['has_account']),
        'no_accounts': sum(1 for e in employee_account_status if not e['has_account']),
        'search_keyword': search_keyword,
    }
    
    return render(request, 'eims_app/user_management.html', context)

@login_required
@user_passes_test(is_superuser)
def sync_user_from_employee(request, employee_id):
    """从员工信息同步创建用户"""
    
    try:
        # 按租户过滤，防止跨租户操作
        if hasattr(request, 'tenant') and request.tenant:
            emp = Employee.objects.get(id=employee_id, tenant_id=request.tenant.id)
        else:
            emp = Employee.objects.get(id=employee_id)
        username = emp.mobile if emp.mobile else emp.name
        
        if User.objects.filter(username=username).exists():
            messages.warning(request, f"用户 {username} 已存在")
        else:
            default_password = 'sc123456#'
            user = User.objects.create_user(
                username=username,
                password=default_password,
                first_name=emp.name,
            )
            user.save()
            messages.success(
                request,
                f"为用户 {emp.name} 创建账号成功，用户名：{username}，初始密码：{default_password}"
            )
    except Exception as e:
        messages.error(request, f"创建失败：{str(e)}")
    
    return redirect('eims_app:user_management')
