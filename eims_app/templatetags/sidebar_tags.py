"""
EIMS 菜单生成标签
路径: eims_app/templatetags/sidebar_tags.py
用途：在模板中动态生成菜单，支持权限控制
"""

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def render_sidebar_menu(context):
    """
    渲染侧边栏菜单
    用法: {% render_sidebar_menu %}
    """
    request = context['request']
    user = request.user
    
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
            'permission': 'eims_app.view_contract'
        },
        {
            'id': 'project',
            'url': reverse('project_list'),
            'text': '项目管理',
            'icon': 'bi-diagram-3',
            'permission': 'eims_app.view_project'
        },
        {
            'id': 'personnel',
            'url': reverse('personnel_list'),
            'text': '人员管理',
            'icon': 'bi-people',
            'permission': 'eims_app.view_personnel'
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
            'id': 'system',
            'url': reverse('admin:index'),
            'text': '系统设置',
            'icon': 'bi-gear',
            'permission': 'is_superuser'  # 特殊权限
        }
    ]
    
    # 过滤用户有权限的菜单
    visible_items = []
    for item in menu_items:
        if item['permission'] == 'is_superuser':
            if user.is_superuser:
                visible_items.append(item)
        elif user.has_perm(item['permission']):
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