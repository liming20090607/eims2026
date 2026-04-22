#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为所有造价咨询子模块的form.html添加项目编号和项目名称显示
"""

import re
import os

# 需要处理的文件列表
FORM_FILES = [
    r'e:\EIMS2026\eims_app\templates\cost_consulting\task_plan\form.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\task_implementation\form.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\review_result\form.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\payment_status\form.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\project_archive\form.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\remuneration_distribution\form.html',
]

def add_project_info_display(content):
    """在编辑模式下添加项目编号和项目名称显示"""
    
    # 查找编辑模式的隐藏项目选择器部分
    pattern = r'(\s+{% else %}\s+<!-- 编辑模式：隐藏项目选择器 -->\s+\{\{ form\.selected_project \}\})'
    
    replacement = r'''\1
                    
                    <!-- 编辑模式：显示项目编号和名称 -->
                    <div class="col-md-6">
                        <label class="form-label text-muted">项目编号</label>
                        <div class="form-control-plaintext fw-bold text-primary">{{ form.instance.project_code|default:"-" }}</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label class="form-label text-muted">项目名称</label>
                        <div class="form-control-plaintext fw-bold">{{ form.instance.project_name|default:"-" }}</div>
                    </div>'''
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("  ✓ 已添加项目编号和名称显示")
        return content
    else:
        print("  ✗ 未找到编辑模式标记，可能结构不同")
        return content


def process_file(file_path):
    """处理单个文件"""
    print(f"\n处理文件: {os.path.basename(os.path.dirname(file_path))}/form.html")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 添加项目编号和名称显示
        content = add_project_info_display(content)
        
        # 如果内容有变化，写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ 文件已更新")
            return True
        else:
            print(f"  ℹ 文件无需修改或已包含该功能")
            return False
            
    except Exception as e:
        print(f"  ✗ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("批量添加项目编号和名称显示到编辑页面")
    print("=" * 80)
    
    success_count = 0
    total_count = len(FORM_FILES)
    
    for file_path in FORM_FILES:
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
