"""
EIMS 上下文处理器
路径: eims_app/context_processors.py
用途：向所有模板注入侧边栏相关变量和全局设置
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
    enabled_module_codes = []  # 当前租户启用的模块代码列表
    enabled_submodule_codes = []  # 当前租户启用的子模块代码列表
    
    if request.user.is_authenticated:
        from eims_app.models.model_contract_approval import ContractApproval
        from eims_app.models.model_seal_approval import SealApproval
        from eims_app.models.model_archive_approval import ArchiveApproval
        from eims_app.models import Tenant, UserProfile
        from eims_app.models.model_tenant_module import TenantModulePermission
        from eims_app.models.model_sub_module import TenantSubModulePermission
        
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
        # 注意：使用 UserTenantRelation 表来查询用户关联的所有公司
        # 这样支持一个用户在多家公司任职
        try:
            from eims_app.models import UserTenantRelation
            
            if request.user.is_superuser:
                # 超级管理员可以看到所有公司（用于切换）
                tenants_all = list(Tenant.objects.filter(is_active=True))
            else:
                # 普通用户只能看到自己关联的公司
                # 通过 UserTenantRelation 表查询用户关联的所有公司
                user_tenant_relations = UserTenantRelation.objects.filter(
                    user=request.user,
                    tenant__is_active=True
                ).select_related('tenant')
                
                tenants_all = [rel.tenant for rel in user_tenant_relations]
                
                # 如果 UserTenantRelation 中没有记录，回退到使用 UserProfile 的 tenant
                if not tenants_all:
                    try:
                        user_profile = UserProfile.objects.get(user=request.user)
                        if user_profile.tenant and user_profile.tenant.is_active:
                            tenants_all = [user_profile.tenant]
                    except UserProfile.DoesNotExist:
                        pass
        except Exception as e:
            # 记录错误但继续执行，避免影响页面加载
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading tenants for user {request.user.username}: {e}")
            tenants_all = []
        
        # 获取当前租户启用的模块列表（独立于租户查询，避免相互影响）
        try:
            current_tenant_id = request.session.get('tenant_id')
            if current_tenant_id:
                enabled_permissions = TenantModulePermission.objects.filter(
                    tenant_id=current_tenant_id,
                    is_enabled=True,
                    module__is_active=True
                ).values_list('module__code', flat=True)
                enabled_module_codes = list(enabled_permissions)
                
                # 如果该租户没有任何模块权限配置，默认启用所有模块
                if not enabled_module_codes:
                    from eims_app.models.model_tenant_module import TenantModule
                    enabled_module_codes = list(
                        TenantModule.objects.filter(is_active=True).values_list('code', flat=True)
                    )
            else:
                # 如果没有选择租户，默认启用所有模块
                from eims_app.models.model_tenant_module import TenantModule
                enabled_module_codes = list(
                    TenantModule.objects.filter(is_active=True).values_list('code', flat=True)
                )
        except Exception as e:
            # 记录错误但继续执行，不影响租户列表
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading module permissions: {e}")
            # 出错时默认启用所有模块
            try:
                from eims_app.models.model_tenant_module import TenantModule
                enabled_module_codes = list(
                    TenantModule.objects.filter(is_active=True).values_list('code', flat=True)
                )
            except:
                enabled_module_codes = []
        
        # 获取当前租户启用的子模块列表
        try:
            current_tenant_id = request.session.get('tenant_id')
            if current_tenant_id:
                enabled_sub_permissions = TenantSubModulePermission.objects.filter(
                    tenant_id=current_tenant_id,
                    is_enabled=True,
                    sub_module__is_active=True
                ).values_list('sub_module__code', flat=True)
                enabled_submodule_codes = list(enabled_sub_permissions)
        except Exception as e:
            # 记录错误但继续执行，不影响主流程
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading sub-module permissions: {e}")
            enabled_submodule_codes = []
    
    return {
        'sidebar_collapsed': sidebar_collapsed,
        'pending_count': pending_count,
        'tenants_all': tenants_all,
        'enabled_module_codes': enabled_module_codes,  # 当前租户启用的模块代码
        'enabled_submodule_codes': enabled_submodule_codes,  # 当前租户启用的子模块代码
        'url_namespace': _get_url_namespace(request),  # 当前URL命名空间
    }


def _get_url_namespace(request):
    """
    根据当前请求路径确定URL命名空间
    """
    path = request.path
    
    # 检查路径前缀
    if path.startswith('/dingce/'):
        return 'dingce'
    elif path.startswith('/shengchang/'):
        return 'shengchang'
    elif path.startswith('/jiachengda/'):
        return 'jiachengda'
    elif path.startswith('/root/'):
        return 'root'
    else:
        # 默认使用 dingce
        return 'dingce'