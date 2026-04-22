"""
修复4个子模块的表头格式
将错误的表头格式统一为正确格式
"""
import re

FILES_TO_FIX = [
    r'e:\EIMS2026\eims_app\templates\cost_consulting\review_result\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\payment_status\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\project_archive\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\remuneration_distribution\list.html',
]

def fix_table_headers(file_path):
    """修复单个文件的表头格式"""
    print(f"\n处理文件: {file_path.split('\\')[-1]}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fix_count = 0
    
    # 匹配错误的表头格式：onclick="handleSort('xxx')" 后面跟着 <span class="sort-icon"></span>
    # 需要替换为正确的格式
    # 注意：class 属性可能包含多个类名（如 "sortable text-end"）
    pattern = r'<th class="([^"]*sortable[^"]*)" data-field="([^"]+)" onclick="handleSort\(\'([^\']+)\'\)">([^<]+)<span class="sort-icon"></span></th>'
    
    def replace_header(match):
        nonlocal fix_count
        fix_count += 1
        classes = match.group(1)
        field = match.group(2)
        field_name = match.group(3)
        display_text = match.group(4)
        
        # 构建正确的表头HTML
        return f'<th class="{classes}" data-field="{field}" onclick="handleSort(\'{field}\', event)">{display_text}<span class="sort-priority"></span><span class="sort-direction"></span><span class="filter-indicator">🔍</span></th>'
    
    content = re.sub(pattern, replace_header, content)
    
    if fix_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 修复了 {fix_count} 个表头")
        return True
    else:
        print(f"  - 无需修复（所有表头格式正确）")
        return False

def main():
    print("=" * 80)
    print("修复造价咨询子模块表头格式")
    print("=" * 80)
    
    success_count = 0
    total_fixed = 0
    
    for file_path in FILES_TO_FIX:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if fix_table_headers(file_path):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"修复完成！成功修复 {success_count} 个文件")
    print("=" * 80)
    
    if success_count > 0:
        print("\n✅ 已修复的子模块：")
        print("  1. 审核成果 (review_result)")
        print("  2. 收费情况 (payment_status)")
        print("  3. 项目存档 (project_archive)")
        print("  4. 酬劳分配 (remuneration_distribution)")
        
        print("\n✨ 修复内容：")
        print("  ✓ 添加 event 参数到 onclick 属性")
        print("  ✓ 将 <span class=\"sort-icon\"></span> 替换为正确的 span 结构")
        print("  ✓ 添加 sort-priority（优先级数字）")
        print("  ✓ 添加 sort-direction（排序方向箭头）")
        print("  ✓ 添加 filter-indicator（筛选漏斗图标）")
        
        print("\n🎯 现在的表头格式：")
        print('  <th class="sortable" data-field="xxx" onclick="handleSort(\'xxx\', event)">')
        print('    字段名')
        print('    <span class="sort-priority"></span>')
        print('    <span class="sort-direction"></span>')
        print('    <span class="filter-indicator">🔍</span>')
        print('  </th>')
