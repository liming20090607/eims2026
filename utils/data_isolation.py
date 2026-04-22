"""
数据隔离工具函数 - 为试用用户过滤测试数据
"""
from django.contrib.auth.models import Group


def is_test_user(user):
    """
    检查用户是否为试用用户
    
    Args:
        user: Django User 对象
        
    Returns:
        bool: True 如果是试用用户，否则 False
    """
    if not user or not user.is_authenticated:
        return False
    
    # 检查用户名是否包含"试用"关键字
    if '试用' in user.username:
        return True
    
    # 或者检查用户组名称
    user_groups = user.groups.all()
    for group in user_groups:
        if '试用' in group.name:
            return True
    
    return False


def filter_queryset_for_test_user(queryset, request, test_prefix='TEST'):
    """
    根据用户类型过滤查询集
    
    Args:
        queryset: Django QuerySet 对象
        request: HTTP Request 对象
        test_prefix: 测试数据前缀标识（默认 'TEST'）
        
    Returns:
        QuerySet: 过滤后的查询集
    """
    user = request.user
    
    # 如果不是试用用户，返回原始查询集
    if not is_test_user(user):
        return queryset
    
    # 对于试用用户，只返回带有 TEST 前缀的数据
    # 根据不同模型的字段进行过滤
    model_name = queryset.model.__name__
    
    # Employee 模型 - 按 employee_code 过滤
    if model_name == 'Employee':
        return queryset.filter(employee_code__startswith=test_prefix)
    
    # ProjectDetail 模型 - 按 project_code 或 contract_code 过滤
    elif model_name == 'ProjectDetail':
        from django.db.models import Q
        return queryset.filter(
            Q(project_code__startswith=test_prefix) | 
            Q(contract_code__startswith=f'HT-{test_prefix}')
        )
    
    # Contract 模型 - 按 contract_code 过滤
    elif model_name == 'Contract':
        return queryset.filter(contract_code__contains=test_prefix)
    
    # Notice 模型 - 按 notice_title 过滤
    elif model_name == 'Notice':
        return queryset.filter(notice_title__contains='测试')
    
    # Personnel 模型 - 按 personnel_code 过滤
    elif model_name == 'Personnel':
        return queryset.filter(personnel_code__startswith=test_prefix)
    
    # FileManage 模型 - 按 file_name 过滤
    elif model_name == 'FileManage':
        return queryset.filter(file_name__contains=test_prefix)
    
    # Department 模型 - 按 department_name 过滤
    elif model_name == 'Department':
        return queryset.filter(department_name__contains='测试')
    
    # 默认：尝试按 code/name/title 字段过滤
    else:
        from django.db.models import Q
        # 获取模型的所有字段
        fields = [f.name for f in queryset.model._meta.get_fields()]
        
        # 尝试常见的标识字段
        filter_conditions = Q()
        for field in ['code', 'name', 'title', 'number']:
            if field in fields:
                filter_conditions |= Q(**{f'{field}__contains': test_prefix})
        
        if filter_conditions:
            return queryset.filter(filter_conditions)
        
        # 如果没有任何匹配字段，返回空查询集
        return queryset.none()
