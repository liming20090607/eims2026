#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量为造价咨询子模块添加筛选漏斗图标和右键菜单功能
"""

import re
import os

# 需要处理的文件列表
FILES_TO_PROCESS = [
    r'e:\EIMS2026\eims_app\templates\cost_consulting\review_result\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\payment_status\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\project_archive\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\remuneration_distribution\list.html',
]

def add_filter_css(content):
    """在CSS中添加筛选漏斗图标样式"""
    
    # 查找未排序时隐藏方向箭头的CSS规则
    pattern = r'(    /\* 未排序时隐藏方向箭头 \*/\s+th\.sortable:not\(\.sorted-asc\):not\(\.sorted-desc\) \.sort-direction \{\s+display: none;\s+\})'
    
    replacement = r'''\1
    
    /* 筛选漏斗图标 */
    th.sortable .filter-indicator {
        display: none;
        margin-left: 4px;
        font-size: 0.85rem;
        vertical-align: middle;
        color: #0d6efd;
        cursor: pointer;
    }
    
    th.sortable.filtered .filter-indicator {
        display: inline-block;
    }
    
    th.sortable.filtered {
        background-color: rgba(13, 110, 253, 0.08) !important;
    }'''
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("  ✓ 已添加筛选漏斗图标CSS样式")
        return content
    else:
        print("  ✗ 未找到CSS插入位置")
        return content


def add_filter_indicator_to_headers(content):
    """在所有sortable表头添加漏斗图标"""
    
    # 匹配所有sortable的th标签（不包含filter-indicator的）
    pattern = r'(<th class="sortable[^"]*" data-field="[^"]+" onclick="handleSort\([^)]+\)">[^<]+<span class="sort-priority"></span><span class="sort-direction"></span>)(</th>)'
    
    def replace_func(match):
        before = match.group(1)
        after = match.group(2)
        # 检查是否已经有filter-indicator
        if 'filter-indicator' not in before:
            return before + '<span class="filter-indicator">🔍</span>' + after
        return match.group(0)
    
    new_content = re.sub(pattern, replace_func, content)
    
    if new_content != content:
        count = len(re.findall(r'filter-indicator', new_content)) - len(re.findall(r'filter-indicator', content))
        print(f"  ✓ 已为 {count} 个表头添加漏斗图标")
        return new_content
    else:
        print("  ℹ 表头已包含漏斗图标或无需添加")
        return content


def add_javascript_functions(content):
    """在updateSortDisplay函数后添加筛选和右键菜单功能"""
    
    # 查找updateSortDisplay函数的结束位置
    pattern = r'(function updateSortDisplay\(\) \{.*?^\})'
    
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if not match:
        print("  ✗ 未找到updateSortDisplay函数")
        return content
    
    # 检查是否已经添加了相关功能
    if 'updateFilterIndicators' in content:
        print("  ℹ JavaScript功能已存在")
        return content
    
    insert_pos = match.end()
    
    javascript_code = '''
    
    // 检测并显示筛选图标
    updateFilterIndicators();
}

// 更新筛选指示器
function updateFilterIndicators() {
    const urlParams = new URLSearchParams(window.location.search);
    
    document.querySelectorAll('th.sortable').forEach(th => {
        const field = th.dataset.field;
        if (field) {
            const filterKey = `filter_${field}`;
            const hasFilter = urlParams.has(filterKey) && urlParams.get(filterKey).trim() !== '';
            
            if (hasFilter) {
                th.classList.add('filtered');
            } else {
                th.classList.remove('filtered');
            }
        }
    });
}

// ==================== 右键菜单功能 ====================
let currentContextMenuField = null;
let currentContextMenuElement = null;

// 创建右键菜单HTML
function createContextMenu() {
    const menu = document.createElement('div');
    menu.id = 'sort-context-menu';
    menu.className = 'sort-context-menu';
    menu.style.display = 'none';
    
    menu.innerHTML = `
        <div class="menu-item" data-action="remove-sort">
            <i class="bi bi-x-circle"></i>
            <span>取消本字段排序</span>
        </div>
        <div class="menu-item" data-action="add-filter">
            <i class="bi bi-funnel"></i>
            <span>按此字段筛选</span>
        </div>
        <div class="menu-item disabled" data-action="remove-filter">
            <i class="bi bi-funnel-fill"></i>
            <span>取消此字段筛选</span>
        </div>
    `;
    
    document.body.appendChild(menu);
    
    // 绑定菜单项点击事件
    menu.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            // 如果是禁用的菜单项，不执行操作
            if (this.classList.contains('disabled')) {
                return;
            }
            const action = this.dataset.action;
            handleContextMenuAction(action);
            hideContextMenu();
        });
    });
    
    return menu;
}

// 显示右键菜单
function showContextMenu(event, field, thElement) {
    event.preventDefault();
    event.stopPropagation();
    
    currentContextMenuField = field;
    currentContextMenuElement = thElement;
    
    let menu = document.getElementById('sort-context-menu');
    if (!menu) {
        menu = createContextMenu();
    }
    
    // 检查该字段是否有筛选条件
    const urlParams = new URLSearchParams(window.location.search);
    const filterKey = `filter_${field}`;
    const hasFilter = urlParams.has(filterKey) && urlParams.get(filterKey).trim() !== '';
    
    // 更新"取消此字段筛选"菜单项的状态
    const removeFilterItem = menu.querySelector('[data-action="remove-filter"]');
    if (removeFilterItem) {
        if (hasFilter) {
            removeFilterItem.classList.remove('disabled');
        } else {
            removeFilterItem.classList.add('disabled');
        }
    }
    
    // 计算菜单位置
    const rect = thElement.getBoundingClientRect();
    const menuWidth = 200;
    const menuHeight = 120;
    
    let left = rect.left + window.scrollX;
    let top = rect.bottom + window.scrollY;
    
    // 确保菜单不超出视口
    if (left + menuWidth > window.innerWidth) {
        left = window.innerWidth - menuWidth - 10;
    }
    if (top + menuHeight > window.innerHeight + window.scrollY) {
        top = rect.top + window.scrollY - menuHeight;
    }
    
    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
    menu.style.display = 'block';
}

// 隐藏右键菜单
function hideContextMenu() {
    const menu = document.getElementById('sort-context-menu');
    if (menu) {
        menu.style.display = 'none';
    }
    currentContextMenuField = null;
    currentContextMenuElement = null;
}

// 处理右键菜单操作
function handleContextMenuAction(action) {
    if (!currentContextMenuField) return;
    
    switch(action) {
        case 'remove-sort':
            removeFromSort(currentContextMenuField);
            break;
        case 'add-filter':
            showFilterDialog(currentContextMenuField);
            break;
        case 'remove-filter':
            removeFilterForField(currentContextMenuField);
            break;
    }
}

// 从排序中移除字段
function removeFromSort(field) {
    const index = sortFields.indexOf(field);
    if (index !== -1) {
        sortFields.splice(index, 1);
        sortOrders.splice(index, 1);
        updateSortUrl();
        updateSortDisplay();
    }
}

// 显示筛选对话框
function showFilterDialog(field) {
    const th = document.querySelector(`th[data-field="${field}"]`);
    if (!th) return;
    
    const fieldName = th.textContent.replace(/[🔍▲▼]/g, '').replace(/\\d+/g, '').trim();
    
    // 获取当前筛选值
    const urlParams = new URLSearchParams(window.location.search);
    const filterKey = `filter_${field}`;
    const operatorKey = `filter_${field}_op`;
    const currentValue = urlParams.get(filterKey) || '';
    const currentOperator = urlParams.get(operatorKey) || 'contains';
    
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">筛选: ${fieldName}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">筛选方式</label>
                        <select class="form-select" id="filter-operator">
                            <option value="contains" ${currentOperator === 'contains' ? 'selected' : ''}>包含</option>
                            <option value="equals" ${currentOperator === 'equals' ? 'selected' : ''}>等于</option>
                            <option value="starts_with" ${currentOperator === 'starts_with' ? 'selected' : ''}>开头是</option>
                            <option value="ends_with" ${currentOperator === 'ends_with' ? 'selected' : ''}>结尾是</option>
                            <option value="not_contains" ${currentOperator === 'not_contains' ? 'selected' : ''}>不包含</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">筛选值</label>
                        <input type="text" class="form-control" id="filter-value" value="${currentValue}" placeholder="请输入筛选值">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                    <button type="button" class="btn btn-danger" onclick="removeFilterForField('${field}')">清除筛选</button>
                    <button type="button" class="btn btn-primary" onclick="applyFilter('${field}')">确定</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // 模态框关闭后清理
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// 应用筛选
function applyFilter(field) {
    const operator = document.getElementById('filter-operator').value;
    const value = document.getElementById('filter-value').value.trim();
    
    const url = new URL(window.location.href);
    
    if (value) {
        url.searchParams.set(`filter_${field}`, value);
        url.searchParams.set(`filter_${field}_op`, operator);
    } else {
        url.searchParams.delete(`filter_${field}`);
        url.searchParams.delete(`filter_${field}_op`);
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

// 取消字段筛选
function removeFilterForField(field) {
    const url = new URL(window.location.href);
    const filterKey = `filter_${field}`;
    const operatorKey = `filter_${field}_op`;
    
    url.searchParams.delete(filterKey);
    url.searchParams.delete(operatorKey);
    url.searchParams.set('page', '1');
    
    window.location.href = url.toString();
}

// 为可排序表头添加右键事件
document.addEventListener('DOMContentLoaded', function() {
    initSortState();
    updateSortDisplay();
    updateFilterIndicators();  // 初始化筛选指示器
    
    // 为所有可排序表头添加右键事件
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('contextmenu', function(e) {
            const field = this.dataset.field;
            if (field) {
                showContextMenu(e, field, this);
            }
        });
    });
    
    // 点击其他地方关闭菜单
    document.addEventListener('click', function() {
        hideContextMenu();
    });
    
    // ESC键关闭菜单
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideContextMenu();
        }
    });
});

// 排序右键菜单样式
const sortMenuStyle = document.createElement('style');
sortMenuStyle.textContent = `
    .sort-context-menu {
        position: absolute;
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        z-index: 9999;
        min-width: 200px;
        padding: 0.5rem 0;
        animation: fadeIn 0.15s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .sort-context-menu .menu-item {
        padding: 0.6rem 1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transition: all 0.2s;
        font-size: 0.9rem;
        color: #212529;
    }
    
    .sort-context-menu .menu-item:hover {
        background-color: #e9ecef;
        color: #0d6efd;
    }
    
    .sort-context-menu .menu-item i {
        font-size: 1rem;
        width: 16px;
        text-align: center;
    }
    
    .sort-context-menu .menu-item:first-child {
        border-bottom: 1px solid #e9ecef;
    }
    
    /* 禁用的菜单项样式 */
    .sort-context-menu .menu-item.disabled {
        opacity: 0.4;
        cursor: not-allowed;
        color: #6c757d;
        pointer-events: none;
    }
    
    .sort-context-menu .menu-item.disabled:hover {
        background-color: transparent;
        color: #6c757d;
    }
`;
document.head.appendChild(sortMenuStyle);'''
    
    # 替换原有的闭合括号和DOMContentLoaded
    old_domContentLoaded = r'''
document\.addEventListener\('DOMContentLoaded', function\(\) \{
    initSortState\(\);
    updateSortDisplay\(\);
\}\);'''
    
    # 先删除原有的简单DOMContentLoaded
    content = re.sub(old_domContentLoaded, '', content)
    
    # 在updateSortDisplay后插入新代码
    content = content[:insert_pos] + javascript_code + content[insert_pos:]
    
    print("  ✓ 已添加JavaScript功能（筛选检测、右键菜单、智能启用/禁用）")
    return content


def process_file(file_path):
    """处理单个文件"""
    print(f"\n处理文件: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 步骤1: 添加CSS样式
        content = add_filter_css(content)
        
        # 步骤2: 添加表头漏斗图标
        content = add_filter_indicator_to_headers(content)
        
        # 步骤3: 添加JavaScript功能
        content = add_javascript_functions(content)
        
        # 如果内容有变化，写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ 文件已更新")
            return True
        else:
            print(f"  ℹ 文件无需修改")
            return False
            
    except Exception as e:
        print(f"  ✗ 处理失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("批量添加筛选漏斗图标和右键菜单功能")
    print("=" * 80)
    
    success_count = 0
    total_count = len(FILES_TO_PROCESS)
    
    for file_path in FILES_TO_PROCESS:
        if os.path.exists(file_path):
            if process_file(file_path):
                success_count += 1
        else:
            print(f"\n✗ 文件不存在: {file_path}")
    
    print("\n" + "=" * 80)
    print(f"处理完成: {success_count}/{total_count} 个文件成功更新")
    print("=" * 80)


if __name__ == '__main__':
    main()
