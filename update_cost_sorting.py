#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量更新造价咨询子模块模板的排序功能为 Django Admin 风格
- 替换 sort-icon 为 sort-priority 和 sort-direction
- 添加 event 参数到 handleSort 调用
- 更新 JavaScript 多字段排序逻辑
"""

import os
import re

TEMPLATES_DIR = r"e:\EIMS2026\eims_app\templates\cost_consulting"

# 需要更新的模板列表（除了 project_info 已更新）
templates_to_update = [
    "task_implementation/list.html",
    "review_result/list.html",
    "payment_status/list.html",
    "project_archive/list.html",
    "remuneration_distribution/list.html",
]

def update_template(file_path):
    """更新单个模板文件"""
    print(f"\n处理: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 更新 HTML 表头：替换 sort-icon 为 sort-priority 和 sort-direction
    # 模式1: 已有 event 参数但 span 还是旧的
    pattern_html1 = r'(onclick="handleSort\([\'\"]([^\'\"]+)[\'\"],\s*event\)">[^<]*<span\s+class="sort-icon"[^>]*></span>)'
        
    def replace_span_only(match):
        onclick = match.group(1)
        field_name = match.group(2)
        return onclick.replace('<span class="sort-icon"></span>', '<span class="sort-priority"></span><span class="sort-direction"></span>')
        
    content = re.sub(pattern_html1, replace_span_only, content)
        
    # 模式2: 缺少 event 参数且 span 是旧的
    pattern_html2 = r'(onclick="handleSort\([\'\"]([^\'\"]+)[\'\"]\)">[^<]*<span\s+class="sort-icon"[^>]*></span>)'
        
    def replace_full(match):
        onclick_part = match.group(1)
        field_name = match.group(2)
        # 添加 event 参数
        new_onclick = onclick_part.replace(f"handleSort('{field_name}')", f"handleSort('{field_name}', event)")
        # 替换 span
        new_onclick = new_onclick.replace('<span class="sort-icon"></span>', '<span class="sort-priority"></span><span class="sort-direction"></span>')
        return new_onclick
        
    content = re.sub(pattern_html2, replace_full, content)
    
    # 2. 更新 JavaScript 排序函数
    # 替换整个排序功能部分
    old_js_pattern = r'//\s*=\s*排序功能[\s\S]*?document\.addEventListener\(\'DOMContentLoaded\'[\s\S]*?initSortDisplay\(\)[\s\S]*?\}\);'
    
    new_js = '''// ==================== 排序功能 (Django Admin 风格 - 多字段排序) ====================
let sortFields = [];
let sortOrders = [];

// 初始化排序状态
function initSortState() {
    const url = new URL(window.location.href);
    const fieldsStr = url.searchParams.get('sort_field');
    const ordersStr = url.searchParams.get('sort_order');
    
    if (fieldsStr) {
        sortFields = fieldsStr.split(',').map(f => f.trim());
        sortOrders = ordersStr ? ordersStr.split(',').map(o => o.trim()) : ['asc'].repeat(sortFields.length);
    } else {
        sortFields = ['created_at'];
        sortOrders = ['desc'];
    }
}

function handleSort(field, event) {
    if (!event) event = window.event;
    
    // 如果按住 Ctrl 或 Shift 键，添加到多字段排序
    if (event && (event.ctrlKey || event.shiftKey)) {
        const existingIndex = sortFields.indexOf(field);
        if (existingIndex !== -1) {
            // 已存在，切换顺序
            sortOrders[existingIndex] = sortOrders[existingIndex] === 'asc' ? 'desc' : 'asc';
        } else {
            // 新字段，添加到末尾
            sortFields.push(field);
            sortOrders.push('asc');
        }
    } else {
        // 单击：设置为唯一排序字段
        if (sortFields[0] === field) {
            // 同一字段，切换顺序
            sortOrders[0] = sortOrders[0] === 'asc' ? 'desc' : 'asc';
        } else {
            // 新字段，替换当前排序
            sortFields = [field];
            sortOrders = ['asc'];
        }
    }
    
    updateSortUrl();
    updateSortDisplay();
}

function updateSortUrl() {
    const url = new URL(window.location.href);
    url.searchParams.set('sort_field', sortFields.join(','));
    url.searchParams.set('sort_order', sortOrders.join(','));
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function updateSortDisplay() {
    // 清除所有排序状态
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
        const priority = th.querySelector('.sort-priority');
        if (priority) priority.textContent = '';
        const direction = th.querySelector('.sort-direction');
        if (direction) direction.style.display = 'none';
    });
    
    // 显示当前排序字段的优先级数字
    sortFields.forEach((field, index) => {
        const th = document.querySelector(`th[data-field="${field}"]`);
        if (th) {
            const order = sortOrders[index];
            th.classList.add(order === 'asc' ? 'sorted-asc' : 'sorted-desc');
            
            const priority = th.querySelector('.sort-priority');
            if (priority) {
                priority.textContent = index + 1;  // 显示优先级数字 1, 2, 3...
                priority.style.display = 'inline-block';
            }
            
            const direction = th.querySelector('.sort-direction');
            if (direction) {
                direction.style.display = 'inline-block';
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initSortState();
    updateSortDisplay();
});'''
    
    content = re.sub(old_js_pattern, new_js, content)
    
    # 保存修改
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已更新: {file_path}")
    else:
        print(f"- 无需更新: {file_path}")

def main():
    print("=" * 70)
    print("批量更新造价咨询子模块排序功能为 Django Admin 风格")
    print("=" * 70)
    
    for template in templates_to_update:
        file_path = os.path.join(TEMPLATES_DIR, template)
        if os.path.exists(file_path):
            update_template(file_path)
        else:
            print(f"\n✗ 文件不存在: {file_path}")
    
    print("\n" + "=" * 70)
    print("批量更新完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
