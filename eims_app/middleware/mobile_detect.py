"""
移动端检测中间件
通过 User-Agent 识别移动设备，为所有用户提供统一的手机版界面
"""
import re


class MobileDetectMiddleware:
    """
    检测移动设备并设置 request.is_mobile 标志。
    
    同时提供 request.is_tablet 用于区分平板设备。
    所有移动设备（含平板）统一使用手机版模板，确保所有用户看到一致的界面。
    
    检测策略（按优先级）：
    1. URL 参数 ?mobile=1/0 强制切换（最高优先级，便于测试）
    2. Session 中存储的移动偏好（一旦识别为移动端则持久化）
    3. 客户端 Cookie（is_mobile=1，由桌面端模板的 JS 视口检测设置）
    4. User-Agent 正则匹配
    5. Client Hints 头（Sec-CH-UA-Mobile）
    """
    
    # 移动端 User-Agent 关键词（更全面的匹配）
    MOBILE_PATTERNS = re.compile(
        r'android|webos|iphone|ipod|blackberry|iemobile|opera mini|'
        r'windows phone|mobile|iphone|ipad|tablet|playbook|silk|'
        r'kindle|lumiya|nokia|samsung|huawei|xiaomi|oppo|vivo|'
        r'oneplus|meizu|smartphone|phone',
        re.IGNORECASE
    )
    
    # 平板 User-Agent 关键词
    TABLET_PATTERNS = re.compile(
        r'ipad|tablet|playbook|silk|kindle',
        re.IGNORECASE
    )
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 1. 检测是否为移动设备（User-Agent 正则）
        is_mobile = bool(self.MOBILE_PATTERNS.search(user_agent))
        is_tablet = bool(self.TABLET_PATTERNS.search(user_agent))
        
        # 2. Client Hints 检测（现代浏览器支持）
        if not is_mobile:
            sec_ch_ua_mobile = request.META.get('HTTP_SEC_CH_UA_MOBILE', '')
            if sec_ch_ua_mobile == '?1':
                is_mobile = True
        
        # 3. Session 持久化：一旦识别为移动端，后续请求保持移动端
        # 这样可以避免某些代理/CDN 改变 User-Agent 导致桌面端模板闪现
        if hasattr(request, 'session'):
            session_mobile = request.session.get('_is_mobile', None)
            if session_mobile is True:
                is_mobile = True
            elif session_mobile is False and not is_mobile:
                # 只有当 session 明确标记为桌面且 UA 也未检测到移动时才用桌面
                pass
        
        # 3.5 客户端 Cookie 检测（由桌面端模板的 JS 视口检测设置）
        # 用于处理"请求桌面版网站"导致 UA 不匹配的情况
        if not is_mobile:
            cookie_mobile = request.COOKIES.get('is_mobile', '')
            if cookie_mobile == '1':
                is_mobile = True
        
        # 平板也统一使用移动端模板
        if is_tablet:
            is_mobile = True
        
        request.is_mobile = is_mobile
        request.is_tablet = is_tablet
        
        # 4. URL 参数强制切换（最高优先级）
        force_mobile = request.GET.get('mobile')
        if force_mobile == '1':
            request.is_mobile = True
            request.is_tablet = False
            if hasattr(request, 'session'):
                request.session['_is_mobile'] = True
        elif force_mobile == '0':
            request.is_mobile = False
            request.is_tablet = False
            if hasattr(request, 'session'):
                request.session['_is_mobile'] = False
        
        # 将检测结果写入 session（仅在确实检测到移动设备时）
        if hasattr(request, 'session') and request.is_mobile:
            request.session['_is_mobile'] = True
        
        response = self.get_response(request)
        return response
