from django.http import HttpResponseRedirect

def login_required_middleware(get_response):
    def middleware(request):
        # 不需要登录的路径
        exempt_urls = [
            '/admin/login/',
            '/accounts/login/',
            '/login/',
            '/forgot-password/',
            '/qr-login/',
            '/wechat-login/',
            '/api/sms/',
            '/api/forgot-password/',
            '/static/',
            '/media/',
            '/tenant/select/',  # 公司选择页面不需要检查租户
            '/tenant/switch/',  # 公司切换
        ]
        
        # 检查是否需要登录
        path = request.path
        if not any(path.startswith(url) for url in exempt_urls):
            if not request.user.is_authenticated:
                return HttpResponseRedirect('/login/')
            
            # 用户已登录，检查是否选择了公司
            if request.user.is_authenticated and hasattr(request, 'session'):
                tenant_id = request.session.get('tenant_id')
                
                # 如果没有选择公司，重定向到公司选择页面
                if not tenant_id:
                    # 但允许访问公司选择页面本身
                    if path != '/tenant/select/':
                        return HttpResponseRedirect('/tenant/select/')
        
        response = get_response(request)
        return response
    return middleware
