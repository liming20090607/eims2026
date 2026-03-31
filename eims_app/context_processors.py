def global_settings(request):
    """
    自定义全局上下文处理器，提供全局模板变量
    所有模板页面均可直接使用这些变量（如{{ SITE_NAME }}）
    """
    return {
        # 网站名称（可修改）
        'SITE_NAME': 'EIMS系统',
        # 网站版本（可修改）
        'SITE_VERSION': '1.0.0',
        # 全局版权信息（可修改）
        'COPYRIGHT': '© 2026 EIMS系统 版权所有',
        # 全局联系方式（可修改）
        'CONTACT_PHONE': '138xxxx8888',
    }
"""
EIMS 上下文处理器
路径: eims_app/context_processors.py
用途：向所有模板注入侧边栏相关变量
"""

def sidebar_context(request):
    """
    向所有模板注入侧边栏状态
    """
    # 从 session 获取折叠状态，无则默认展开
    # 安全检查：确保 session 可用
    try:
        sidebar_collapsed = request.session.get('sidebar_collapsed', False)
    except (AttributeError, KeyError):
        sidebar_collapsed = False
    
    return {
        'sidebar_collapsed': sidebar_collapsed
    }