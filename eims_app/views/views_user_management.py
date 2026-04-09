import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q
from eims_app.models import Employee
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
    
    # 获取所有员工（基础查询集）
    employees = Employee.objects.filter(is_deleted=False)
    
    # 如果有搜索关键词，进行模糊搜索
    if search_keyword:
        # 搜索员工信息（姓名、职位、公司）
        employees = employees.filter(
            Q(name__icontains=search_keyword) |
            Q(admin_position__icontains=search_keyword) |
            Q(tenant__name__icontains=search_keyword)
        )
    
    employees = employees.order_by('employee_code')
    
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
        if user:
            user_groups = list(user.groups.all().values_list('name', flat=True))
            user_group_ids = list(user.groups.all().values_list('id', flat=True))
            # 获取用户所属公司
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
        })
    
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
        
        elif action == 'update_user_groups':
            # 更新用户组
            user_id = request.POST.get('user_id')
            group_ids = request.POST.getlist('group_ids')
            
            try:
                from django.contrib.auth.models import Group
                user = User.objects.get(id=user_id)
                
                # 清空现有组
                user.groups.clear()
                
                # 添加新组
                if group_ids:
                    groups = Group.objects.filter(id__in=group_ids)
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
    from django.contrib.auth.models import Group
    all_groups = Group.objects.all().order_by('name')
    
    context = {
        'employee_account_status': employee_account_status,
        'form': form,
        'password_reset_form': password_reset_form,
        'all_groups': all_groups,
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
