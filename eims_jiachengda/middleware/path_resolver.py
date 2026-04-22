"""
Path Resolver Middleware
Identifies which company system is being accessed based on URL path and sets request.current_system.
"""


class PathResolverMiddleware:
    """
    Middleware that parses the URL path to determine which company system is being accessed.
    
    Sets request.current_system to one of:
    - 'dingce' for /dingce/ paths
    - 'shengchang' for /shengchang/ paths
    - 'jiachengda' for /jiachengda/ paths
    - 'root' for /root/ paths
    - None for other paths (will be handled by route selector)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract the first path component
        path = request.path_info.lstrip('/')
        
        if path.startswith('dingce'):
            request.current_system = 'dingce'
            request.company_name = '广西鼎策工程顾问有限责任公司'
        elif path.startswith('shengchang'):
            request.current_system = 'shengchang'
            request.company_name = '广西晟昌工程科技有限责任公司'
        elif path.startswith('jiachengda'):
            request.current_system = 'jiachengda'
            request.company_name = '广西嘉诚达工程造价咨询有限公司'
        elif path.startswith('root') or path.startswith('admin'):
            # Admin pages and root admin both use root_admin database
            request.current_system = 'root'
            request.company_name = '超级管理员后台'
        else:
            request.current_system = None
            request.company_name = None
        
        response = self.get_response(request)
        return response
