"""
权限检查装饰器和工具函数
用于控制用户对特定功能的访问
"""

from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


def permission_required(permission_code, login_url=None, raise_exception=False):
    """
    权限检查装饰器
    
    :param permission_code: 权限代码，如 'eims_app.view_department'
    :param login_url: 登录页面 URL，默认 None
    :param raise_exception: 是否抛出异常，默认 False（返回 JSON 提示）
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 检查用户是否已登录
            if not request.user.is_authenticated:
                if raise_exception:
                    raise PermissionDenied("用户未登录")
                return JsonResponse({
                    'success': False,
                    'message': '用户未登录，请先登录！'
                }, status=401)
            
            # 检查用户是否有权限
            has_permission = request.user.has_perm(permission_code)
            
            # 超级管理员拥有所有权限
            if request.user.is_superuser:
                has_permission = True
            
            if not has_permission:
                if raise_exception:
                    raise PermissionDenied("权限不足")
                
                # 返回 JSON 格式的权限不足提示
                return JsonResponse({
                    'success': False,
                    'message': '权限不足，请于管理员联系！',
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def superuser_required(view_func):
    """
    超级用户权限检查装饰器
    仅允许超级管理员访问
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': '用户未登录，请先登录！'
            }, status=401)
        
        if not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': '权限不足，请于管理员联系！',
                'code': 'SUPERUSER_REQUIRED'
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ajax_permission_required(permission_code):
    """
    AJAX 请求的权限检查装饰器
    专门用于处理 AJAX 请求的权限验证
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': '用户未登录，请先登录！'
                }, status=401)
            
            if not request.user.has_perm(permission_code) and not request.user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'message': '权限不足，请于管理员联系！',
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
