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
        ]
        
        # 检查是否需要登录
        path = request.path
        if not any(path.startswith(url) for url in exempt_urls):
            if not request.user.is_authenticated:
                return HttpResponseRedirect('/login/')
        
        response = get_response(request)
        return response
    return middleware
