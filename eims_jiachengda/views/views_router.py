"""
Route Selector View
Intelligently routes users to the appropriate company system based on their permissions.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserProfile


@login_required
def route_selector(request):
    """
    Route selector that determines where to send the user based on their company affiliations.
    
    Rules:
    1. Superusers (root) -> /root/ admin dashboard
    2. Users with one company -> Auto-redirect to that company's system
    3. Users with multiple companies -> Show company selection page
    4. Users with no companies -> Show no permission page
    """
    user = request.user
    
    # Rule 1: Root/superuser goes to admin backend
    if user.is_superuser:
        return redirect('/root/')
    
    # Get user's profile and associated tenants
    try:
        user_profile = UserProfile.objects.get(user=user)
        user_tenants = Tenant.objects.filter(userprofile=user_profile).distinct()
    except UserProfile.DoesNotExist:
        return render(request, 'eims_app/no_permission.html', {
            'message': '用户资料不存在，请联系管理员。'
        })
    
    tenant_count = user_tenants.count()
    
    # Rule 4: No company permissions
    if tenant_count == 0:
        return render(request, 'eims_app/no_permission.html', {
            'message': '您尚未被分配到任何公司，请联系管理员分配权限。'
        })
    
    # Rule 2: Single company - auto redirect
    elif tenant_count == 1:
        tenant = user_tenants.first()
        tenant_name = tenant.name
        
        if '鼎策' in tenant_name or 'dingce' in tenant_name.lower():
            return redirect('/dingce/')
        elif '晟昌' in tenant_name or 'shengchang' in tenant_name.lower():
            return redirect('/shengchang/')
        elif '嘉诚达' in tenant_name or 'jiachengda' in tenant_name.lower():
            return redirect('/jiachengda/')
        elif 'root' in tenant_name.lower() or tenant.code.lower() == 'root_admin':
            return redirect('/root/')
        else:
            # Default fallback - try to match by tenant code
            return redirect(f'/{tenant.code}/')
    
    # Rule 3: Multiple companies - show selection page
    else:
        # Prepare tenant list with routing information
        tenant_list = []
        for tenant in user_tenants:
            tenant_info = {
                'id': tenant.id,
                'name': tenant.name,
                'url': None,
                'icon': 'building'
            }
            
            # Determine URL based on company name
            if '鼎策' in tenant.name or 'dingce' in tenant.name.lower():
                tenant_info['url'] = '/dingce/'
                tenant_info['color'] = 'primary'
            elif '晟昌' in tenant.name or 'shengchang' in tenant.name.lower():
                tenant_info['url'] = '/shengchang/'
                tenant_info['color'] = 'success'
            elif '嘉诚达' in tenant.name or 'jiachengda' in tenant.name.lower():
                tenant_info['url'] = '/jiachengda/'
                tenant_info['color'] = 'info'
            else:
                tenant_info['url'] = '#'
                tenant_info['color'] = 'secondary'
            
            tenant_list.append(tenant_info)
        
        return render(request, 'eims_app/tenant_select.html', {
            'tenants': tenant_list,
            'username': user.username,
            'full_name': user.get_full_name() or user.username
        })
