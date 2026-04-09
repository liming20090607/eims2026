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
        
        if not tenant_id:
            messages.error(request, '请选择一个公司')
            return render(request, 'eims_app/tenant_select.html', {
                'tenants': tenants
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
        'tenants': tenants
    })


@login_required
def tenant_switch(request):
    """
    快速切换公司（从侧边栏或其他地方调用）
    """
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        
        if tenant_id:
            try:
                selected_tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                user_profile = UserProfile.objects.get(user=request.user)
                
                # 验证权限
                if request.user.is_superuser or user_profile.tenant == selected_tenant:
                    request.session['tenant_id'] = selected_tenant.id
                    user_profile.tenant = selected_tenant
                    user_profile.save(update_fields=['tenant'])
                    messages.success(request, f'已切换到：{selected_tenant.name}')
                else:
                    messages.error(request, '您没有权限访问该公司')
                    
            except Tenant.DoesNotExist:
                messages.error(request, '公司不存在')
    
    # 返回到来源页面
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
