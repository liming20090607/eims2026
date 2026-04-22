#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复分页链接中的转义引号问题
将 \' 替换为 '
"""

import os
import re

TEMPLATES_DIR = r"e:\EIMS2026\eims_app\templates\cost_consulting"

templates_to_fix = [
    "payment_status/list.html",
    "project_archive/list.html",
    "remuneration_distribution/list.html",
]

def fix_template(file_path):
    """修复单个模板文件"""
    print(f"\n处理: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 修复转义引号
    content = content.replace("\\'", "'")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已修复")
        return True
    else:
        print(f"- 无需修复")
        return False

def main():
    print("=" * 80)
    print("修复分页链接中的转义引号")
    print("=" * 80)
    
    success_count = 0
    for template in templates_to_fix:
        file_path = os.path.join(TEMPLATES_DIR, template)
        if os.path.exists(file_path):
            if fix_template(file_path):
                success_count += 1
        else:
            print(f"✗ 文件不存在: {file_path}")
    
    print("\n" + "=" * 80)
    print(f"完成！成功修复 {success_count}/{len(templates_to_fix)} 个文件")
    print("=" * 80)

if __name__ == "__main__":
    main()
