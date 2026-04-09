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
    tenants_all = []
    
    if request.user.is_authenticated:
        from eims_app.models.model_contract_approval import ContractApproval
        from eims_app.models.model_seal_approval import SealApproval
        from eims_app.models.model_archive_approval import ArchiveApproval
        from eims_app.models import Tenant, UserProfile
        
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
        
        # 获取用户可访问的所有公司（用于切换公司下拉列表）
        # 注意：这里返回所有活跃公司，因为切换公司时用户需要看到所有可选的公司
        # 但数据查询时会按当前选中的租户过滤
        try:
            if request.user.is_superuser:
                # 超级管理员可以看到所有公司（用于切换）
                tenants_all = list(Tenant.objects.filter(is_active=True))
            else:
                # 普通用户只能看到自己所属的公司
                user_profile = UserProfile.objects.get(user=request.user)
                tenants_all = list(Tenant.objects.filter(
                    is_active=True,
                    userprofile=user_profile
                ))
        except Exception as e:
            # 记录错误但继续执行，避免影响页面加载
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading tenants for user {request.user.username}: {e}")
            tenants_all = []
    
    return {
        'sidebar_collapsed': sidebar_collapsed,
        'pending_count': pending_count,
        'tenants_all': tenants_all,
    }