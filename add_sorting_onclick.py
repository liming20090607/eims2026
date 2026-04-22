#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量为造价咨询子模块的可排序表头添加 onclick 事件处理器
"""

import os
import re

TEMPLATES_DIR = r"e:\EIMS2026\eims_app\templates\cost_consulting"

# 需要修复的模板列表
templates_to_fix = [
    "project_info/list.html",
    "task_plan/list.html",
    "task_implementation/list.html",
    "review_result/list.html",
    "payment_status/list.html",
    "project_archive/list.html",
    "remuneration_distribution/list.html",
]

def add_onclick_to_headers(file_path):
    """为可排序表头添加 onclick 事件"""
    print(f"\n处理: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 匹配所有带有 class="sortable" 和 data-field 但没有 onclick 的 th 标签
    # 模式：<th class="sortable" data-field="xxx">...</th>
    pattern = r'(<th\s+class="sortable"[^>]*)\s+data-field="([^"]+)"([^>]*>)'
    
    def replace_th(match):
        before_data_field = match.group(1)
        field_name = match.group(2)
        after_data_field = match.group(3)
        
        # 检查是否已经有 onclick
        if 'onclick=' in before_data_field or 'onclick=' in after_data_field:
            return match.group(0)  # 已有 onclick，不修改
        
        # 构建新的 th 标签，在 data-field 后添加 onclick
        return f'{before_data_field} data-field="{field_name}" onclick="handleSort(\'{field_name}\', event)"{after_data_field}'
    
    content = re.sub(pattern, replace_th, content)
    
    # 也处理带 text-end 类的情况
    pattern2 = r'(<th\s+class="sortable\s+text-end"[^>]*)\s+data-field="([^"]+)"([^>]*>)'
    
    def replace_th2(match):
        before_data_field = match.group(1)
        field_name = match.group(2)
        after_data_field = match.group(3)
        
        # 检查是否已经有 onclick
        if 'onclick=' in before_data_field or 'onclick=' in after_data_field:
            return match.group(0)  # 已有 onclick，不修改
        
        # 构建新的 th 标签
        return f'{before_data_field} data-field="{field_name}" onclick="handleSort(\'{field_name}\', event)"{after_data_field}'
    
    content = re.sub(pattern2, replace_th2, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 统计添加了多少个 onclick
        onclick_count = len(re.findall(r'onclick="handleSort\(', content))
        print(f"  ✓ 已添加 {onclick_count} 个 onclick 事件处理器")
        return True
    else:
        print("  - 无需修改（可能已经添加了 onclick）")
        return False

def main():
    print("=" * 80)
    print("批量添加 onclick 事件到造价咨询子模块的可排序表头")
    print("=" * 80)
    
    success_count = 0
    skip_count = 0
    
    for template_path in templates_to_fix:
        full_path = os.path.join(TEMPLATES_DIR, template_path)
        if os.path.exists(full_path):
            if add_onclick_to_headers(full_path):
                success_count += 1
            else:
                skip_count += 1
        else:
            print(f"\n✗ 文件不存在: {full_path}")
    
    print("\n" + "=" * 80)
    print(f"修复完成！成功: {success_count}, 跳过: {skip_count}")
    print("=" * 80)
    
    if success_count > 0:
        print("\n✅ 已修复的子模块：")
        for i, template in enumerate(templates_to_fix, 1):
            print(f"  {i}. {template}")
        
        print("\n✨ 修复内容：")
        print("  ✓ 为所有 class='sortable' 的 th 标签添加 onclick 事件")
        print("  ✓ onclick 调用 handleSort(field_name, event)")
        print("  ✓ 保留原有的 data-field 属性")
        print("  ✓ 避免重复添加（如果已有 onclick 则跳过）")
        
        print("\n🎯 现在的行为：")
        print("  - 点击表头 → 触发排序")
        print("  - 第一次点击 → 升序排列")
        print("  - 再次点击同一字段 → 降序排列")
        print("  - 点击不同字段 → 多字段排序（新字段优先级最高）")

if __name__ == '__main__':
    main()
