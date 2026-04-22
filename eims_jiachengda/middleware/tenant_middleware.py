"""
租户中间件 - 自动识别和管理当前租户
用于多租户数据隔离
"""
from eims_app.models import Tenant
from django.shortcuts import redirect
from django.urls import reverse


class TenantMiddleware:
    """
    租户中间件 - 在请求对象上存储当前租户信息
    
    工作流程：
    1. 从 session 中读取 tenant_id
    2. 查询对应的 Tenant 对象
    3. 将 tenant 对象附加到 request 对象上
    4. 后续视图可以通过 request.tenant 访问当前租户
    5. 如果用户已登录但没有选择公司，重定向到公司选择页面
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 在请求处理之前执行
        # 从 session 中获取 tenant_id
        tenant_id = None
        
        if hasattr(request, 'session'):
            tenant_id = request.session.get('tenant_id')
        
        # 查询租户对象
        if tenant_id:
            try:
                request.tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                # 租户不存在或已禁用，清除 session
                request.tenant = None
                if hasattr(request, 'session'):
                    if 'tenant_id' in request.session:
                        del request.session['tenant_id']
        else:
            request.tenant = None
        
        # 调用下一个中间件或视图
        response = self.get_response(request)
        
        return response
