"""
EIMS 菜单生成标签
路径: eims_app/templatetags/sidebar_tags.py
用途：在模板中动态生成菜单，支持权限控制和租户模块配置
"""

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from eims_app.models.model_user import UserProfile

register = template.Library()

@register.simple_tag(takes_context=True)
def render_sidebar_menu(context):
    """
    渲染侧边栏菜单
    用法: {% render_sidebar_menu %}
    """
    request = context['request']
    user = request.user
    
    # 获取当前用户的租户（公司）
    tenant = None
    try:
        profile = UserProfile.objects.get(user=user)
        tenant = profile.tenant
    except (UserProfile.DoesNotExist, AttributeError):
        pass
    
    # 获取租户启用的模块代码列表
    enabled_module_codes = []
    if tenant:
        from eims_app.models.model_tenant_module import TenantModulePermission
        permissions = TenantModulePermission.objects.filter(tenant=tenant, is_enabled=True)
        enabled_module_codes = [p.module.code for p in permissions]
    
    # 如果是超级管理员，启用所有模块
    if user.is_superuser:
        from eims_app.models.model_tenant_module import TenantModule
        enabled_module_codes = [m.code for m in TenantModule.objects.filter(is_active=True)]
    
    # 模块代码与菜单项ID的映射关系
    MODULE_MENU_MAP = {
        'supervision': ['contract', 'project'],  # 工程监理：显示合同管理、项目管理
    }
    
    # 如果未配置任何模块，默认启用所有（向后兼容）
    if not enabled_module_codes:
        enabled_module_codes = ['preparation', 'bidding', 'design', 'cost', 'supervision', 'construction', 'testing']
    
    # 根据启用的模块，获取应该显示的菜单项ID列表
    enabled_menu_ids = set()
    for module_code in enabled_module_codes:
        menu_ids = MODULE_MENU_MAP.get(module_code, [])
        enabled_menu_ids.update(menu_ids)
    
    # 始终显示的基础菜单（不受模块控制）
    base_menu_ids = {'dashboard', 'employee', 'personnel', 'file_manage', 'notice', 'monthly_report', 'system'}
    enabled_menu_ids.update(base_menu_ids)
    
    # 定义菜单项（与menu_config.js保持一致）
    menu_items = [
        {
            'id': 'dashboard',
            'url': reverse('dashboard'),  # 需在urls.py中定义命名路由
            'text': '仪表盘',
            'icon': 'bi-speedometer2',
            'permission': 'eims_app.view_dashboard'
        },
        {
            'id': 'contract',
            'url': reverse('contract_list'),
            'text': '合同管理',
            'icon': 'bi-file-earmark-text',
            'permission': 'eims_app.view_contract',
            'has_submenu': True,
            'submenu_items': [
                {'url': reverse('contract_list'), 'text': '合同台账', 'icon': 'bi-journal-text'},
                {'url': reverse('contract_approval_chain'), 'text': '审批流程', 'icon': 'bi-diagram-3'},
                {'url': reverse('my_pending_approvals'), 'text': '我的待审批', 'icon': 'bi-bell-fill', 'badge': True},
                {'url': reverse('my_initiated_approvals'), 'text': '我发起的', 'icon': 'bi-send'},
            ]
        },
        {
            'id': 'project',
            'url': reverse('project_list'),
            'text': '项目管理',
            'icon': 'bi-building',
            'permission': 'eims_app.view_project',
            'has_submenu': True,
            'submenu_items': [
                {'url': reverse('project_ledger_list'), 'text': '项目台账', 'icon': 'bi-journal-text'},
                {'url': reverse('contract_management_list'), 'text': '合同管理', 'icon': 'bi-file-earmark-text'},
                {'url': reverse('output_payment_list'), 'text': '产值回款', 'icon': 'bi-cash-coin'},
            ]
        },
        {
            'id': 'employee',
            'url': reverse('eims_app:employee_list'),
            'text': '员工信息',
            'icon': 'bi-person-badge',
            'permission': 'is_superuser'
        },
        {
            'id': 'personnel',
            'url': reverse('personnel_list'),
            'text': '人员管理',
            'icon': 'bi-people',
            'permission': 'eims_app.view_personnel'
        },
        {
            'id': 'output_payment',
            'url': reverse('output_payment_list'),
            'text': '产值回款',
            'icon': 'bi-cash-coin',
            'permission': 'eims_app.view_output_payment'
        },
        {
            'id': 'file_manage',
            'url': reverse('file_manage_list'),
            'text': '文件管理',
            'icon': 'bi-folder',
            'permission': 'eims_app.view_file_manage'
        },
        {
            'id': 'notice',
            'url': reverse('notice_list'),
            'text': '通知公告',
            'icon': 'bi-bell',
            'permission': 'eims_app.view_notice'
        },
        {
            'id': 'monthly_report',
            'url': reverse('eims_app:monthly_report_list'),
            'text': '月度报告',
            'icon': 'bi-calendar-check',
            'permission': 'eims_app.view_monthly_report'
        },
        {
            'id': 'system',
            'url': reverse('admin:index'),
            'text': '系统设置',
            'icon': 'bi-gear',
            'permission': 'is_superuser'  # 特殊权限
        }
    ]
    
    # 过滤用户有权限的菜单，并根据租户模块配置进行筛选
    visible_items = []
    for item in menu_items:
        # 检查用户权限
        has_permission = False
        if item['permission'] == 'is_superuser':
            has_permission = user.is_superuser
        elif user.has_perm(item['permission']):
            has_permission = True
        
        # 检查租户是否启用了该模块对应的菜单
        menu_enabled = item['id'] in enabled_menu_ids
        
        # 只有同时满足用户权限和模块启用条件才显示
        if has_permission and menu_enabled:
            visible_items.append(item)
    
    # 生成HTML
    html = '<ul id="sidebar-menu" class="nav flex-column">'
    
    for item in visible_items:
        # 检查当前URL是否匹配（高亮）
        is_active = request.path.startswith(item['url'])
        
        html += f'''
        <li class="nav-item">
          <a href="{item['url']}" 
             class="nav-link {'active' if is_active else ''}"
             data-tooltip="{item['text']}">
            <span class="menu-icon"><i class="bi {item['icon']}"></i></span>
            <span class="menu-text">{item['text']}</span>
          </a>
        </li>
        '''
    
    if not visible_items:
        html += '''
        <li class="nav-item text-center py-4">
          <span class="text-muted">无可用菜单</span>
        </li>
        '''
    
    html += '</ul>'
    
    return mark_safe(html)