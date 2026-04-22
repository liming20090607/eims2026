#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复造价咨询子模块中缺少 event 参数的 onclick 事件
"""

import os
import re

TEMPLATES_DIR = r"e:\EIMS2026\eims_app\templates\cost_consulting"

# 需要检查的模板列表
templates_to_check = [
    "task_implementation/list.html",
    "review_result/list.html",
    "payment_status/list.html",
    "remuneration_distribution/list.html",
]

def fix_missing_event_param(file_path):
    """修复缺少 event 参数的 onclick"""
    print(f"\n处理: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 匹配 onclick="handleSort('xxx')" 但没有 event 参数的情况
    pattern = r'onclick="handleSort\(\'([^\']+)\'\)"'
    
    def replace_onclick(match):
        field_name = match.group(1)
        return f'onclick="handleSort(\'{field_name}\', event)"'
    
    content = re.sub(pattern, replace_onclick, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 统计修复了多少个
        fixed_count = len(re.findall(r'onclick="handleSort\([^,]+,\s*event\)"', content))
        print(f"  ✓ 已修复 {fixed_count} 个 onclick 事件（添加了 event 参数）")
        return True
    else:
        print("  - 无需修改（所有 onclick 都已包含 event 参数）")
        return False

def main():
    print("=" * 80)
    print("修复造价咨询子模块中缺少的 event 参数")
    print("=" * 80)
    
    success_count = 0
    skip_count = 0
    
    for template_path in templates_to_check:
        full_path = os.path.join(TEMPLATES_DIR, template_path)
        if os.path.exists(full_path):
            if fix_missing_event_param(full_path):
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
        for i, template in enumerate(templates_to_check, 1):
            print(f"  {i}. {template}")
        
        print("\n✨ 修复内容：")
        print("  ✓ 为所有 handleSort(field) 添加 event 参数")
        print("  ✓ 统一为 handleSort(field, event)")
        print("  ✓ 确保漏斗图标检测功能正常工作")

if __name__ == '__main__':
    main()
