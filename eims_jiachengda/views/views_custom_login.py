"""
自定义登录视图 - 支持公司选择
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from eims_app.models import Tenant, UserProfile
from django.db.models import Q


def custom_login(request):
    """
    自定义登录视图，支持：
    1. 用户名/姓名自动匹配
    2. 多公司任职时提示选择
    3. 单公司时自动选择
    """
    
    # 如果用户已登录，直接跳转到首页
    if request.user.is_authenticated:
        return redirect('eims_app:eims_index')
    
    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        tenant_id = request.POST.get('tenant_id', '')
        
        if not username_input or not password:
            messages.error(request, '请输入用户名和密码')
            return render(request, 'login.html', {'show_tenant_select': False})
        
        # 尝试查找用户（支持用户名、姓名、邮箱）
        user = None
        try:
            # 首先尝试精确匹配用户名
            user = User.objects.get(username=username_input)
        except User.DoesNotExist:
            # 尝试匹配姓名
            users_by_name = User.objects.filter(
                Q(first_name=username_input) | Q(last_name=username_input)
            )
            if users_by_name.count() == 1:
                user = users_by_name.first()
            elif users_by_name.count() > 1:
                # 多个同名用户，需要进一步确认
                messages.error(request, f'找到多个名为"{username_input}"的用户，请使用用户名登录')
                return render(request, 'login.html', {'show_tenant_select': False})
        
        # 如果还是没找到，尝试邮箱
        if not user:
            try:
                user = User.objects.get(email=username_input)
            except User.DoesNotExist:
                pass
        
        if not user:
            messages.error(request, '用户不存在')
            return render(request, 'login.html', {'show_tenant_select': False})
        
        # 验证密码
        user = authenticate(request, username=user.username, password=password)
        
        if user is None:
            messages.error(request, '密码错误')
            return render(request, 'login.html', {'show_tenant_select': False})
        
        # 获取用户的租户信息
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # 如果没有UserProfile，创建一个
            user_profile = UserProfile.objects.create(user=user)
        
        # 获取用户有权限访问的所有公司
        if user.is_superuser:
            # 超级管理员可以看到所有公司
            available_tenants = Tenant.objects.filter(is_active=True)
        else:
            # 普通用户只能看到自己所属的公司
            available_tenants = Tenant.objects.filter(
                is_active=True,
                userprofile=user_profile
            )
        
        tenant_count = available_tenants.count()
        
        # 情况1：用户没有分配任何公司
        if tenant_count == 0:
            messages.error(request, '您还没有被分配到任何公司，请联系管理员')
            return render(request, 'login.html', {'show_tenant_select': False})
        
        # 情况2：用户只属于一个公司
        if tenant_count == 1:
            selected_tenant = available_tenants.first()
            request.session['tenant_id'] = selected_tenant.id
            user_profile.tenant = selected_tenant
            user_profile.save(update_fields=['tenant'])
            
            # 登录用户
            login(request, user)
            messages.success(request, f'✓ 登录成功！已自动选择公司：{selected_tenant.name}')
            
            # 超级管理员进入root后台，普通用户进入对应公司系统
            if user.is_superuser:
                return redirect('/root/')
            else:
                # 根据租户代码跳转到对应系统
                tenant_code = selected_tenant.code
                if tenant_code == 'dingce':
                    return redirect('/dingce/')
                elif tenant_code == 'shengchang':
                    return redirect('/shengchang/')
                elif tenant_code == 'jiachengda':
                    # 嘉诚达用户登录后直接进入造价咨询的项目信息子模块
                    return redirect('/jiachengda/cost_project_info/')
                else:
                    return redirect(f'/{tenant_code}/')
        
        # 情况3：用户属于多个公司，需要选择
        if tenant_count > 1:
            # 如果用户已经提交了公司选择
            if tenant_id:
                try:
                    selected_tenant = available_tenants.get(id=tenant_id)
                    request.session['tenant_id'] = selected_tenant.id
                    user_profile.tenant = selected_tenant
                    user_profile.save(update_fields=['tenant'])
                    
                    # 登录用户
                    login(request, user)
                    messages.success(request, f'✓ 登录成功！已选择公司：{selected_tenant.name}')
                    
                    # 根据租户代码跳转到对应系统
                    tenant_code = selected_tenant.code
                    if tenant_code == 'dingce':
                        return redirect('/dingce/')
                    elif tenant_code == 'shengchang':
                        return redirect('/shengchang/')
                    elif tenant_code == 'jiachengda':
                        # 嘉诚达用户登录后直接进入造价咨询的项目信息子模块
                        return redirect('/jiachengda/cost_project_info/')
                    else:
                        return redirect(f'/{tenant_code}/')
                except Tenant.DoesNotExist:
                    messages.error(request, '无效的公司选择')
            
            # 显示公司选择界面
            return render(request, 'login.html', {
                'show_tenant_select': True,
                'available_tenants': available_tenants,
                'username': username_input,  # 保留用户名，避免重新输入
                'user_display_name': user.get_full_name() or user.username
            })
    
    # GET请求，显示登录表单
    return render(request, 'login.html', {'show_tenant_select': False})
