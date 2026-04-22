"""
租户（公司）选择视图
用于用户登录后选择要操作的公司
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from eims_app.models import Tenant, UserProfile


@login_required
def tenant_select(request):
    """
    公司选择页面
    用户登录后如果没有选择公司，或者想切换公司时访问此页面
    """
    user_profile = UserProfile.objects.get(user=request.user)
    
    # 如果是超级管理员，可以看到所有公司
    if request.user.is_superuser:
        tenants = Tenant.objects.filter(is_active=True)
    else:
        # 普通用户只能看到自己所属的公司
        tenants = Tenant.objects.filter(
            is_active=True,
            userprofile=user_profile
        )
    
    # 如果用户只有一个公司，自动选择并跳转
    if tenants.count() == 1:
        selected_tenant = tenants.first()
        request.session['tenant_id'] = selected_tenant.id
        user_profile.tenant = selected_tenant
        user_profile.save(update_fields=['tenant'])
        messages.success(request, f'已自动选择公司：{selected_tenant.name}')
        return redirect('eims_app:eims_index')
    
    # 处理POST请求（用户选择了公司）
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        password = request.POST.get('password', '')  # 获取密码
        
        if not tenant_id:
            messages.error(request, '请选择一个公司')
            return render(request, 'eims_app/tenant_select.html', {
                'tenants': tenants
            })
        
        # 验证密码（除了超级管理员外都需要密码）
        if not request.user.is_superuser and not password:
            messages.error(request, '请输入登录密码以验证身份')
            return render(request, 'eims_app/tenant_select.html', {
                'tenants': tenants,
                'require_password': True
            })
        
        # 如果需要密码验证，检查密码是否正确
        if not request.user.is_superuser:
            if not request.user.check_password(password):
                messages.error(request, '密码错误，请重新输入')
                return render(request, 'eims_app/tenant_select.html', {
                    'tenants': tenants,
                    'require_password': True
                })
        
        try:
            selected_tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            
            # 验证用户是否有权限访问该公司
            if not request.user.is_superuser:
                if user_profile.tenant != selected_tenant and selected_tenant not in tenants:
                    messages.error(request, '您没有权限访问该公司')
                    return render(request, 'eims_app/tenant_select.html', {
                        'tenants': tenants
                    })
            
            # 保存选择到 session
            request.session['tenant_id'] = selected_tenant.id
            
            # 更新用户的默认公司
            user_profile.tenant = selected_tenant
            user_profile.save(update_fields=['tenant'])
            
            messages.success(request, f'✓ 已切换到：{selected_tenant.name}')
            
            # 跳转到首页或之前访问的页面
            next_url = request.GET.get('next', 'eims_app:eims_index')
            return redirect(next_url)
            
        except Tenant.DoesNotExist:
            messages.error(request, '公司不存在或已禁用')
    
    return render(request, 'eims_app/tenant_select.html', {
        'tenants': tenants,
        'require_password': not request.user.is_superuser  # 非超级管理员需要密码
    })


@login_required
def tenant_switch(request):
    """
    快速切换公司（从侧边栏或其他地方调用）
    需要密码验证
    """
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        password = request.POST.get('password', '')  # 获取密码
        
        if not tenant_id:
            messages.error(request, '请选择要切换的公司')
            referer = request.META.get('HTTP_REFERER', '/')
            return redirect(referer)
        
        # 验证密码（超级管理员除外）
        if not request.user.is_superuser:
            if not password:
                messages.error(request, '请输入登录密码以验证身份')
                referer = request.META.get('HTTP_REFERER', '/')
                return redirect(referer)
            
            if not request.user.check_password(password):
                messages.error(request, '密码错误，切换失败')
                referer = request.META.get('HTTP_REFERER', '/')
                return redirect(referer)
        
        try:
            selected_tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            user_profile = UserProfile.objects.get(user=request.user)
            
            # 验证权限
            if request.user.is_superuser or user_profile.tenant == selected_tenant:
                request.session['tenant_id'] = selected_tenant.id
                user_profile.tenant = selected_tenant
                user_profile.save(update_fields=['tenant'])
                messages.success(request, f'✓ 已切换到：{selected_tenant.name}')
            else:
                messages.error(request, '您没有权限访问该公司')
                
        except Tenant.DoesNotExist:
            messages.error(request, '公司不存在')
    
    # 返回到来源页面
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)


@login_required
def tenant_list(request):
    """
    租户（公司）管理页面 - Root超级管理员专属
    查看所有和编辑公司信息
    """
    # 只有超级管理员才能访问
    if not request.user.is_superuser:
        messages.error(request, '您没有权限访问此页面')
        return redirect('eims_app:eims_index')
    
    # 获取所有租户
    tenants = Tenant.objects.all().order_by('code')
    
    # 统计每个公司的用户数和项目数
    tenant_stats = []
    for tenant in tenants:
        stats = {
            'id': tenant.id,
            'code': tenant.code,
            'name': tenant.name,
            'short_name': tenant.short_name,
            'is_active': tenant.is_active,
            'user_count': tenant.get_active_user_count(),
            'project_count': tenant.get_project_count(),
            'create_time': tenant.create_time,
        }
        tenant_stats.append(stats)
    
    return render(request, 'eims_app/tenant_list.html', {
        'tenants': tenant_stats,
        'total_count': tenants.count(),
    })
