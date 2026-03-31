"""
模板标签：权限检查工具
用于在模板中检查用户权限，控制菜单显示状态
"""

from django import template

register = template.Library()

@register.filter(name='has_perm')
def has_perm_filter(user, permission_code):
    """
    检查用户是否有指定权限（用作过滤器）
    
    用法：{{ request.user|has_perm:'eims_app.add_filemanage' }}
    
    返回：True/False
    """
    if not user or not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    # 检查权限
    return user.has_perm(permission_code)

@register.simple_tag(takes_context=True)
def check_permission(context, permission_code):
    """
    检查用户是否有指定权限
    
    用法：{% check_permission 'eims_app.view_department' as has_perm %}
    
    返回：True/False
    """
    request = context.get('request')
    if not request:
        return False
    
    user = request.user
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    # 检查权限
    return user.has_perm(permission_code)


@register.simple_tag(takes_context=True)
def has_module_permission(context, module_name):
    """
    检查用户是否有模块访问权限
    
    用法：{% has_module_permission 'department' as can_access %}
    
    返回：'full' (完全访问), 'readonly' (只读), 'none' (无权限)
    """
    request = context.get('request')
    if not request:
        return 'none'
    
    user = request.user
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return 'full'
    
    # 定义模块与权限的映射
    module_permissions = {
        'department': ['eims_app.view_department'],
        'contract': ['eims_app.view_contract'],
        'project': ['eims_app.view_project'],
        'personnel': ['eims_app.view_personnel'],
        'file_manage': ['eims_app.view_filemanage'],
        'notice': ['eims_app.view_notice'],
        'approval_chain': ['eims_app.view_approvalchain'],
        'department_role': ['eims_app.view_departmentrole'],
    }
    
    permissions = module_permissions.get(module_name, [])
    
    # 如果没有配置权限要求，默认允许访问
    if not permissions:
        return 'full'
    
    # 检查是否有查看权限（只读）
    has_view = any(user.has_perm(perm) for perm in permissions if 'view' in perm)
    
    # 检查是否有编辑权限（完全访问）
    has_edit = any(user.has_perm(perm) for perm in permissions if 'change' in perm or 'add' in perm or 'delete' in perm)
    
    if has_edit:
        return 'full'
    elif has_view:
        return 'readonly'
    else:
        return 'none'


@register.simple_tag
def check_monthly_report_permission(user):
    """
    检查用户是否有创建月度报告的权限
    仅允许：超级管理员、管理员、主任、副主任、主管、总监
    
    用法：{% check_monthly_report_permission request.user as can_create %}
    
    返回：True/False
    """
    if not user or not user.is_authenticated:
        return False
    
    # 超级管理员直接允许
    if user.is_superuser:
        return True
    
    # 检查部门角色
    from eims_app.models.model_department import DepartmentRole
    from django.db.models import Q
    
    # 允许的角色类型
    allowed_roles = ['manager', 'deputy', 'supervisor']  # 部门经理、副职、主管
    
    # 检查是否有允许的角色类型
    has_allowed_role = DepartmentRole.objects.filter(
        user=user,
        role_type__in=allowed_roles
    ).exists()
    
    # 检查是否是主任、副主任、总监
    has_director_role = DepartmentRole.objects.filter(
        user=user
    ).filter(
        Q(role_name__icontains='主任') | 
        Q(role_name__icontains='副主任') |
        Q(role_name__icontains='总监')
    ).exists()
    
    return has_allowed_role or has_director_role
