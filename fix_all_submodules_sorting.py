"""
批量修复造价咨询子模块的排序功能
将所有子模块的 handleSort 函数统一为项目信息的正确逻辑
"""
import os
import re

# 定义要修复的文件列表
FILES_TO_FIX = [
    r'e:\EIMS2026\eims_app\templates\cost_consulting\task_plan\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\task_implementation\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\review_result\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\payment_status\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\project_archive\list.html',
    r'e:\EIMS2026\eims_app\templates\cost_consulting\remuneration_distribution\list.html',
]

# 正确的 handleSort 函数（来自项目信息）
CORRECT_HANDLE_SORT = '''function handleSort(field, event) {
    if (!event) event = window.event;
    
    // 如果点击的是漏斗图标，不触发排序
    if (event && (event.target.classList.contains('filter-indicator') || event.target.closest('.filter-indicator'))) {
        console.log('点击了漏斗图标，不触发排序');
        return;
    }
    
    // 防止事件冒泡
    if (event) {
        event.stopPropagation();
    }
    
    const existingIndex = sortFields.indexOf(field);
    
    if (existingIndex !== -1) {
        // 字段已存在，获取当前排序方向
        const currentOrder = sortOrders[existingIndex];
        // 将其移到末尾（最高优先级）
        sortFields.splice(existingIndex, 1);
        sortOrders.splice(existingIndex, 1);
        sortFields.push(field);
        // 切换排序方向并添加到末尾
        sortOrders.push(currentOrder === 'asc' ? 'desc' : 'asc');
    } else {
        // 新字段，添加到末尾（最后添加的优先级最高，显示为1）
        sortFields.push(field);
        sortOrders.push('asc');
    }
    
    console.log('排序字段:', sortFields);
    console.log('排序方向:', sortOrders);
    
    updateSortUrl();
    // 注意：updateSortDisplay() 在页面重新加载后由 initSortState() 调用，所以这里不需要调用
}'''

# 错误的 handleSort 函数模式（需要替换的）
WRONG_HANDLE_SORT_PATTERN = r'function handleSort\(field, event\) \{[^}]*if \(!event\) event = window\.event;[^}]*const existingIndex = sortFields\.indexOf\(field\);[^}]*if \(existingIndex !== -1\) \{[^}]*// 字段已存在，切换顺序[^}]*sortOrders\[existingIndex\] = sortOrders\[existingIndex\] === \'asc\' \? \'desc\' : \'asc\';[^}]*\} else \{[^}]*// 新字段，添加到末尾（最后添加的优先级最高，显示为1）[^}]*sortFields\.push\(field\);[^}]*sortOrders\.push\(\'asc\'\);[^}]*\}[^}]*updateSortUrl\(\);[^}]*updateSortDisplay\(\);[^}]*\}'

def fix_handle_sort(file_path):
    """修复单个文件的 handleSort 函数"""
    print(f"\n处理文件: {os.path.basename(file_path)}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换 handleSort 函数
    # 使用更宽松的匹配模式
    pattern = r'function handleSort\(field, event\) \{[\s\S]*?updateSortUrl\(\);[\s\S]*?updateSortDisplay\(\);[\s\S]*?\}'
    
    match = re.search(pattern, content)
    if match:
        old_function = match.group(0)
        print(f"  ✓ 找到旧的 handleSort 函数")
        
        # 替换为正确的函数
        new_content = content.replace(old_function, CORRECT_HANDLE_SORT)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✓ 已更新为正确的 handleSort 函数")
        return True
    else:
        print(f"  ✗ 未找到 handleSort 函数")
        return False

def main():
    print("=" * 80)
    print("批量修复造价咨询子模块排序功能")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for file_path in FILES_TO_FIX:
        if os.path.exists(file_path):
            if fix_handle_sort(file_path):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"\n✗ 文件不存在: {file_path}")
            fail_count += 1
    
    print("\n" + "=" * 80)
    print(f"修复完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 80)
    
    if success_count > 0:
        print("\n✅ 已修复的子模块：")
        print("  1. 任务计划 (task_plan)")
        print("  2. 任务实施 (task_implementation)")
        print("  3. 审核成果 (review_result)")
        print("  4. 收费情况 (payment_status)")
        print("  5. 项目存档 (project_archive)")
        print("  6. 酬劳分配 (remuneration_distribution)")
        
        print("\n✨ 修复内容：")
        print("  ✓ handleSort 函数逻辑统一为项目信息的正确版本")
        print("  ✓ 添加漏斗图标检测（点击漏斗不触发排序）")
        print("  ✓ 添加事件冒泡阻止")
        print("  ✓ 字段已存在时：移到末尾（最高优先级）+ 切换顺序")
        print("  ✓ 新字段：添加到末尾（最高优先级）")
        print("  ✓ 移除 updateSortDisplay() 调用（避免重复渲染）")
        
        print("\n🎯 现在的行为：")
        print("  - 点击字段A → A(1)")
        print("  - 点击字段B → B(1) A(2)")
        print("  - 再次点击A → A(1) B(2) [A切换到降序]")
        print("  - 点击字段C → C(1) A(2) B(3)")

if __name__ == "__main__":
    main()
