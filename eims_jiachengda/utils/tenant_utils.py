"""
租户工具函数 - 用于多租户数据隔离的辅助函数
"""


def get_queryset_for_tenant(model_class, request):
    """
    根据当前租户过滤查询集
    
    参数：
        model_class: 模型类
        request: HTTP 请求对象（包含 tenant 属性）
    
    返回：
        已过滤的 QuerySet
    
    用法：
        projects = get_queryset_for_tenant(ProjectDetail, request)
    """
    queryset = model_class.objects.all()
    
    # 所有用户（包括超级管理员）都按租户过滤
    if hasattr(request, 'tenant') and request.tenant:
        if hasattr(model_class, 'tenant'):
            # 使用 tenant_id 而不是 tenant 对象来避免跨数据库 JOIN
            # Tenant 表在 root_admin 数据库，而业务数据在各公司数据库
            queryset = queryset.filter(tenant_id=request.tenant.id)
        else:
            # 如果模型没有 tenant 字段（如 Tenant 本身），返回所有数据
            pass
    
    return queryset


def filter_queryset_by_tenant(queryset, request):
    """
    过滤已有的查询集（用于已经构建了查询集的场景）
    
    参数：
        queryset: 已有的 QuerySet
        request: HTTP 请求对象（包含 tenant 属性）
    
    返回：
        已过滤的 QuerySet
    
    用法：
        projects = ProjectDetail.objects.filter(status='active')
        projects = filter_queryset_by_tenant(projects, request)
    """
    # 所有用户（包括超级管理员）都按租户过滤
    if hasattr(request, 'tenant') and request.tenant:
        if hasattr(queryset.model, 'tenant'):
            # 使用 tenant_id 而不是 tenant 对象来避免跨数据库 JOIN
            # Tenant 表在 root_admin 数据库，而业务数据在各公司数据库
            queryset = queryset.filter(tenant_id=request.tenant.id)
    
    return queryset


def assign_tenant_to_object(obj, request):
    """
    为对象自动分配租户（在保存前调用）
    
    参数：
        obj: 模型实例
        request: HTTP 请求对象
    
    用法：
        project = ProjectDetail()
        assign_tenant_to_object(project, request)
        project.save()
    """
    if hasattr(obj, 'tenant') and hasattr(request, 'tenant'):
        obj.tenant = request.tenant
    return obj
