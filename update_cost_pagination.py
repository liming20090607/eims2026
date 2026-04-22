#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量更新造价咨询子模块模板的分页链接，支持多字段排序
- 添加 getSortParams() JavaScript 函数
- 更新分页链接使用动态排序参数
"""

import os
import re

TEMPLATES_DIR = r"e:\EIMS2026\eims_app\templates\cost_consulting"

# 需要更新的模板列表（除了 project_info 和 task_implementation 已更新）
templates_to_update = [
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
    
    # 1. 在 <script> 标签后添加 getSortParams 函数
    script_pattern = r'(<script>\s*\n)(// Update batch actions|// 更新批量操作)'
    replacement = r'\1// 获取当前排序参数（用于分页链接）\nfunction getSortParams() {\n    return \'sort_field=\' + sortFields.join(\',\') + \'&sort_order=\' + sortOrders.join(\',\');\n}\n\n\2'
    content = re.sub(script_pattern, replacement, content)
    
    # 2. 更新分页链接 - 首页
    content = re.sub(
        r'href="\?page=1&search=\{\{\s*search_key\s*\}\}&[^\"]*&sort_field=\{\{\s*sort_field\s*\}\}&sort_order=\{\{\s*sort_order\s*\}\}"',
        r'href="javascript:void(0)" onclick="window.location.href=\'?page=1&search={{ search_key }}&\' + getSortParams()"',
        content
    )
    
    # 3. 更新分页链接 - 上一页
    content = re.sub(
        r'href="\?page=\{\{\s*page_obj\.previous_page_number\s*\}\}&search=\{\{\s*search_key\s*\}\}&[^\"]*&sort_field=\{\{\s*sort_field\s*\}\}&sort_order=\{\{\s*sort_order\s*\}\}"',
        r'href="javascript:void(0)" onclick="window.location.href=\'?page={{ page_obj.previous_page_number }}&search={{ search_key }}&\' + getSortParams()"',
        content
    )
    
    # 4. 更新分页链接 - 下一页
    content = re.sub(
        r'href="\?page=\{\{\s*page_obj\.next_page_number\s*\}\}&search=\{\{\s*search_key\s*\}\}&[^\"]*&sort_field=\{\{\s*sort_field\s*\}\}&sort_order=\{\{\s*sort_order\s*\}\}"',
        r'href="javascript:void(0)" onclick="window.location.href=\'?page={{ page_obj.next_page_number }}&search={{ search_key }}&\' + getSortParams()"',
        content
    )
    
    # 5. 更新分页链接 - 末页
    content = re.sub(
        r'href="\?page=\{\{\s*page_obj\.paginator\.num_pages\s*\}\}&search=\{\{\s*search_key\s*\}\}&[^\"]*&sort_field=\{\{\s*sort_field\s*\}\}&sort_order=\{\{\s*sort_order\s*\}\}"',
        r'href="javascript:void(0)" onclick="window.location.href=\'?page={{ page_obj.paginator.num_pages }}&search={{ search_key }}&\' + getSortParams()"',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已更新")
        return True
    else:
        print(f"- 无需更新")
        return False

def main():
    print("=" * 80)
    print("批量更新造价咨询子模块模板的分页链接")
    print("=" * 80)
    
    success_count = 0
    for template in templates_to_update:
        file_path = os.path.join(TEMPLATES_DIR, template)
        if os.path.exists(file_path):
            if update_template(file_path):
                success_count += 1
        else:
            print(f"✗ 文件不存在: {file_path}")
    
    print("\n" + "=" * 80)
    print(f"完成！成功更新 {success_count}/{len(templates_to_update)} 个文件")
    print("=" * 80)

if __name__ == "__main__":
    main()
