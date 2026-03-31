/**
 * EIMS 侧边栏交互核心 (Django 静态文件)
 * 路径: static/js/eims_sidebar.js
 * 依赖：Bootstrap 5 (项目已包含)
 */

class EIMSSidebar {
  constructor() {
    this.sidebar = document.getElementById('eims-sidebar');
    this.toggleBtn = document.getElementById('toggle-sidebar-btn');
    this.isCollapsed = false;
    this.init();
  }

  init() {
    if (!this.sidebar || !this.toggleBtn) {
      console.warn('[EIMS Sidebar] 未找到侧边栏元素，跳过初始化');
      return;
    }
    
    // 1. 恢复上次折叠状态
    this.loadState();
    
    // 2. 绑定折叠按钮
    this.toggleBtn.addEventListener('click', () => this.toggle());
    
    // 3. 监听窗口大小变化
    window.addEventListener('resize', () => this.handleResize());
    
    // 4. 初始化无障碍属性
    this.updateA11y();
    
    // 5. 首次渲染菜单（确保menu_config.js已加载）
    if (typeof renderEIMSMenu === 'function') {
      renderEIMSMenu();
    }
    
    console.log('[EIMS Sidebar] 初始化成功');
  }

  toggle() {
    this.isCollapsed = !this.isCollapsed;
    this.sidebar.classList.toggle('collapsed', this.isCollapsed);
    document.body.classList.toggle('sidebar-collapsed', this.isCollapsed);
    
    // 更新按钮图标
    const icon = this.toggleBtn.querySelector('i');
    if (icon) {
      icon.textContent = this.isCollapsed ? 'chevron_right' : 'chevron_left';
    }
    
    this.toggleBtn.setAttribute('aria-expanded', String(!this.isCollapsed));
    this.toggleBtn.title = this.isCollapsed ? '展开菜单' : '收起菜单';
    
    // 更新Tooltip状态
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('collapsed-tooltip', this.isCollapsed);
    });
    
    // 保存状态
    this.saveState();
    this.updateA11y();
  }

  loadState() {
    const saved = localStorage.getItem('eims_sidebar_collapsed');
    if (saved !== null) {
      this.isCollapsed = saved === 'true';
      if (this.isCollapsed) {
        this.sidebar.classList.add('collapsed');
        document.body.classList.add('sidebar-collapsed');
      }
    }
    // 小屏设备默认折叠
    if (window.innerWidth < 992) {
      this.isCollapsed = true;
      this.sidebar.classList.add('collapsed');
      document.body.classList.add('sidebar-collapsed');
    }
  }

  saveState() {
    localStorage.setItem('eims_sidebar_collapsed', String(this.isCollapsed));
  }

  handleResize() {
    if (window.innerWidth >= 992) {
      // 大屏：恢复保存的状态
      document.body.classList.toggle('sidebar-collapsed', this.isCollapsed);
    } else {
      // 小屏：强制折叠
      this.isCollapsed = true;
      this.sidebar.classList.add('collapsed');
      document.body.classList.add('sidebar-collapsed');
      this.saveState();
    }
  }

  updateA11y() {
    this.sidebar.setAttribute('aria-expanded', String(!this.isCollapsed));
    
    // 为屏幕阅读器更新状态
    const statusEl = document.getElementById('sidebar-status');
    if (statusEl) {
      statusEl.textContent = this.isCollapsed ? '菜单已收起' : '菜单已展开';
    }
  }

  // 外部可调用方法
  expand() {
    if (this.isCollapsed) this.toggle();
  }
  
  collapse() {
    if (!this.isCollapsed) this.toggle();
  }
}

// ======================
// 【自动初始化】
// ======================
document.addEventListener('DOMContentLoaded', () => {
  // 确保DOM元素存在再初始化
  if (document.getElementById('eims-sidebar')) {
    window.eimsSidebar = new EIMSSidebar();
  }
});

// ======================
// 【辅助函数】页面加载后执行
// ======================
window.addEventListener('load', () => {
  // 确保用户权限已注入
  if (window.userPermissions && typeof renderEIMSMenu === 'function') {
    renderEIMSMenu();
  }
});