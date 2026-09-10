"""
移动端检测中间件
通过 User-Agent 识别移动设备，为所有用户提供统一的手机版界面
"""
import re


class MobileDetectMiddleware:
    """
    检测移动设备并设置 request.is_mobile 标志。
    
    同时提供 request.is_tablet 用于区分平板设备。
    所有移动设备统一使用手机版模板，确保所有用户看到一致的界面。
    """
    
    # 移动端 User-Agent 关键词
    MOBILE_PATTERNS = re.compile(
        r'android|webos|iphone|ipod|blackberry|iemobile|opera mini|'
        r'windows phone|mobile|iphone|ipad',
        re.IGNORECASE
    )
    
    # 平板 User-Agent 关键词
    TABLET_PATTERNS = re.compile(
        r'ipad|tablet|playbook|silk',
        re.IGNORECASE
    )
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 检测是否为移动设备
        is_mobile = bool(self.MOBILE_PATTERNS.search(user_agent))
        is_tablet = bool(self.TABLET_PATTERNS.search(user_agent))
        
        request.is_mobile = is_mobile
        request.is_tablet = is_tablet and not is_mobile
        
        # 支持通过 URL 参数强制切换移动端/桌面端（方便测试）
        force_mobile = request.GET.get('mobile')
        if force_mobile == '1':
            request.is_mobile = True
        elif force_mobile == '0':
            request.is_mobile = False
            request.is_tablet = False
        
        response = self.get_response(request)
        return response
