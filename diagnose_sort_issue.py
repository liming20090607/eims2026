"""
诊断项目信息列表排序显示问题
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, r'e:\EIMS2026')

def check_template():
    """检查模板文件中的排序相关代码"""
    template_path = r'e:\EIMS2026\eims_app\templates\cost_consulting\project_info\list.html'
    
    print("=" * 80)
    print("项目信息列表排序功能诊断")
    print("=" * 80)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: 是否有 sortable 类
    sortable_count = content.count('class="sortable"')
    print(f"\n✓ 检查1: 找到 {sortable_count} 个可排序列")
    
    # 检查2: 是否有 sort-priority span
    priority_count = content.count('<span class="sort-priority">')
    print(f"✓ 检查2: 找到 {priority_count} 个优先级徽章元素")
    
    # 检查3: 是否有 sort-direction span
    direction_count = content.count('<span class="sort-direction">')
    print(f"✓ 检查3: 找到 {direction_count} 个方向箭头元素")
    
    # 检查4: 是否有 handleSort 函数
    has_handle_sort = 'function handleSort(field, event)' in content
    print(f"✓ 检查4: handleSort 函数存在: {has_handle_sort}")
    
    # 检查5: 是否有 updateSortDisplay 函数
    has_update_display = 'function updateSortDisplay()' in content
    print(f"✓ 检查5: updateSortDisplay 函数存在: {has_update_display}")
    
    # 检查6: 是否有 DOMContentLoaded 事件监听
    has_dom_ready = "document.addEventListener('DOMContentLoaded'" in content
    print(f"✓ 检查6: DOMContentLoaded 监听器存在: {has_dom_ready}")
    
    # 检查7: 提取所有 data-field 属性
    import re
    data_fields = re.findall(r'data-field="([^"]+)"', content)
    print(f"\n✓ 检查7: 找到 {len(data_fields)} 个数据字段:")
    for i, field in enumerate(data_fields[:10], 1):  # 只显示前10个
        print(f"   {i}. {field}")
    if len(data_fields) > 10:
        print(f"   ... 还有 {len(data_fields) - 10} 个字段")
    
    # 检查8: 验证 created_at 字段是否存在
    has_created_at = 'data-field="created_at"' in content
    print(f"\n✓ 检查8: created_at 字段存在: {has_created_at}")
    
    # 检查9: 查看 updateSortDisplay 函数的关键逻辑
    update_func_match = re.search(
        r'function updateSortDisplay\(\)\s*\{(.*?)\n\}',
        content,
        re.DOTALL
    )
    
    if update_func_match:
        func_body = update_func_match.group(1)
        
        # 检查是否设置 priority.textContent
        sets_priority = 'priority.textContent = index + 1' in func_body
        print(f"\n✓ 检查9: 设置优先级数字逻辑: {sets_priority}")
        
        # 检查是否显示 priority
        shows_priority = "priority.style.display = 'inline-block'" in func_body
        print(f"✓ 检查10: 显示优先级徽章: {shows_priority}")
        
        # 检查是否清除优先级
        clears_priority = "priority.textContent = ''" in func_body
        print(f"✓ 检查11: 清除优先级逻辑: {clears_priority}")
    
    print("\n" + "=" * 80)
    print("诊断结论:")
    print("=" * 80)
    
    all_checks = [
        sortable_count > 0,
        priority_count > 0,
        direction_count > 0,
        has_handle_sort,
        has_update_display,
        has_dom_ready,
        has_created_at,
        sets_priority if 'sets_priority' in locals() else False,
        shows_priority if 'shows_priority' in locals() else False,
    ]
    
    if all(all_checks):
        print("✅ 所有检查通过！代码结构正确。")
        print("\n可能的问题原因:")
        print("1. 浏览器缓存了旧版本的JavaScript")
        print("2. 页面加载时URL中没有排序参数，使用默认字段但没有点击触发")
        print("3. JavaScript执行顺序问题")
        print("\n建议的解决方案:")
        print("1. 硬刷新页面 (Ctrl+F5)")
        print("2. 打开浏览器开发者工具 (F12)，查看Console是否有错误")
        print("3. 在Console中运行: console.log(sortFields, sortOrders) 查看当前状态")
        print("4. 尝试点击任意表头，看是否显示优先级数字")
    else:
        print("❌ 发现问题！请检查上述失败的检查项。")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    check_template()
