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
    向所有模板注入侧边栏状态和待审批数量
    """
    # 从 session 获取折叠状态，无则默认展开
    # 安全检查：确保 session 可用
    try:
        sidebar_collapsed = request.session.get('sidebar_collapsed', False)
    except (AttributeError, KeyError):
        sidebar_collapsed = False
    
    # 计算待审批数量（合同+用印+归档）
    pending_count = 0
    if request.user.is_authenticated:
        from eims_app.models.model_contract_approval import ContractApproval
        from eims_app.models.model_seal_approval import SealApproval
        from eims_app.models.model_archive_approval import ArchiveApproval
        
        contract_count = ContractApproval.objects.filter(
            current_approver=request.user,
            status__in=['pending', 'reviewing'],
            is_deleted=False
        ).count()
        seal_count = SealApproval.objects.filter(
            current_approver=request.user,
            status__in=['pending', 'reviewing'],
            is_deleted=False
        ).count()
        archive_count = ArchiveApproval.objects.filter(
            current_approver=request.user,
            status__in=['pending', 'reviewing'],
            is_deleted=False
        ).count()
        pending_count = contract_count + seal_count + archive_count
    
    return {
        'sidebar_collapsed': sidebar_collapsed,
        'pending_count': pending_count,
    }