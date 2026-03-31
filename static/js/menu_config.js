/**
 * EIMS 菜单配置 (Django 静态文件)
 * 路径: static/js/menu_config.js
 * 用途：定义菜单结构，与Django权限系统对接
 */

// ======================
// 【配置区】菜单数据结构
// ======================
window.EIMS_MENU_ITEMS = [
  {
    id: 'dashboard',
    path: '/dashboard/',
    text: '仪表盘',
    icon: '<i class="bi bi-speedometer2"></i>',
    permission: 'view_dashboard', // 对应Django权限
    order: 1
  },
  {
    id: 'contract',
    path: '/contract/',
    text: '合同管理',
    icon: '<i class="bi bi-file-earmark-text"></i>',
    permission: 'view_contract',
    order: 2
  },
  {
    id: 'project',
    path: '/project/',
    text: '项目管理',
    icon: '<i class="bi bi-diagram-3"></i>',
    permission: 'view_project',
    order: 3
  },
  {
    id: 'personnel',
    path: '/personnel/',
    text: '人员管理',
    icon: '<i class="bi bi-people"></i>',
    permission: 'view_personnel',
    order: 4
  },
  {
    id: 'output_payment',
    path: '/output_payment/',
    text: '产值回款',
    icon: '<i class="bi bi-cash-coin"></i>',
    permission: 'view_output_payment',
    order: 5
  },
  {
    id: 'inspection',
    path: '/inspection/',
    text: '巡检管理',
    icon: '<i class="bi bi-binoculars"></i>',
    permission: 'view_inspection',
    order: 6
  },
  {
    id: 'info_collect',
    path: '/info_collect/',
    text: '信息收集',
    icon: '<i class="bi bi-collection"></i>',
    permission: 'view_info_collect',
    order: 7
  },
  {
    id: 'file_manage',
    path: '/file_manage/',
    text: '文件管理',
    icon: '<i class="bi bi-folder"></i>',
    permission: 'view_file_manage',
    order: 8
  },
  {
    id: 'notice',
    path: '/notice/',
    text: '通知公告',
    icon: '<i class="bi bi-bell"></i>',
    permission: 'view_notice',
    order: 9
  },
  {
    id: 'system',
    path: '/admin/',
    text: '系统设置',
    icon: '<i class="bi bi-gear"></i>',
    permission: 'is_superuser', // 特殊权限：仅管理员
    order: 99
  }
];

// ======================
// 【核心函数】渲染菜单
// ======================
function renderEIMSMenu() {
  const menuContainer = document.getElementById('sidebar-menu');
  if (!menuContainer || !window.userPermissions) return;
  
  // 1. 过滤：仅保留用户有权限的菜单项
  const userMenus = window.EIMS_MENU_ITEMS.filter(item => {
    // 特殊处理超级管理员
    if (item.permission === 'is_superuser' && window.userPermissions.is_superuser) {
      return true;
    }
    // 普通权限检查
    return window.userPermissions[item.permission] === true;
  }).sort((a, b) => a.order - b.order);
  
  // 2. 生成HTML
  let html = '';
  const currentPath = window.location.pathname;
  
  userMenus.forEach(item => {
    // 判断当前页面是否为激活状态
    const isActive = currentPath.startsWith(item.path) || 
                     (currentPath === '/' && item.path === '/dashboard/');
    
    // 为折叠状态准备Tooltip
    const tooltipAttr = `data-tooltip="${item.text}"`;
    
    html += `
      <li class="nav-item">
        <a href="${item.path}" 
           class="nav-link ${isActive ? 'active' : ''} ${window.sidebarCollapsed ? 'collapsed-tooltip' : ''}"
           ${tooltipAttr}
           aria-current="${isActive ? 'page' : undefined}">
          <span class="menu-icon">${item.icon}</span>
          <span class="menu-text">${item.text}</span>
        </a>
      </li>
    `;
  });
  
  // 3. 注入DOM
  menuContainer.innerHTML = html || `
    <li class="nav-item text-center py-4">
      <span class="text-muted">无可用菜单</span>
    </li>
  `;
  
  console.log('[EIMS Sidebar] 菜单渲染完成，共显示', userMenus.length, '项');
}