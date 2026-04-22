"""
统一分页功能样式
将人员花名册的分页样式应用到所有列表页面
"""
import os
import re

def update_pagination_style(file_path, description=""):
    """更新单个文件的分页样式"""
    if not os.path.exists(file_path):
        print(f"⚠️  文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 标准分页HTML模板（带统计信息）
    standard_pagination = '''                {% if page_obj.paginator.num_pages > 1 or page_obj.number == 1 %}
                <div class="pagination-wrapper" style="flex-shrink: 0; background: #f8f9fc; border-top: 1px solid #e3e6f0; padding: 0.4rem 0; box-shadow: none; position: relative; z-index: 10; margin-top: 0; width: 100%;">
                    <nav aria-label="分页导航">
                        <div class="pagination-container">
                            <!-- 统计信息 - 靠左 -->
                            <div class="statistics-info" style="position: absolute; left: 1rem; white-space: nowrap;">
                                <span>总记录: <strong class="text-primary">{{ page_obj.paginator.count }}</strong> 条</span>
                                <span class="ms-2">当前页: <strong class="text-success">{{ page_obj.number }}</strong> / {{ page_obj.paginator.num_pages }}</span>
                                <span class="ms-2">本页: <strong class="text-info">{{ page_obj|length }}</strong> 条</span>
                            </div>
                            
                            <!-- 分页导航 - 居中 -->
                            {% if page_obj.has_previous %}
                            <a href="?page=1{% if search_keyword %}&search={{ search_keyword }}{% endif %}" class="pagination-btn">
                                <i class="bi bi-chevron-double-left"></i> 首页
                            </a>
                            <a href="?page={{ page_obj.previous_page_number }}{% if search_keyword %}&search={{ search_keyword }}{% endif %}" class="pagination-btn">
                                <i class="bi bi-chevron-left"></i> 上一页
                            </a>
                            {% else %}
                            <span class="pagination-btn disabled">
                                <i class="bi bi-chevron-double-left"></i> 首页
                            </span>
                            <span class="pagination-btn disabled">
                                <i class="bi bi-chevron-left"></i> 上一页
                            </span>
                            {% endif %}
                            
                            <span class="pagination-info">
                                第 {{ page_obj.number }} / {{ page_obj.paginator.num_pages }} 页
                            </span>
                            
                            {% if page_obj.has_next %}
                            <a href="?page={{ page_obj.next_page_number }}{% if search_keyword %}&search={{ search_keyword }}{% endif %}" class="pagination-btn">
                                下一页 <i class="bi bi-chevron-right"></i>
                            </a>
                            <a href="?page={{ page_obj.paginator.num_pages }}{% if search_keyword %}&search={{ search_keyword }}{% endif %}" class="pagination-btn">
                                末页 <i class="bi bi-chevron-double-right"></i>
                            </a>
                            {% else %}
                            <span class="pagination-btn disabled">
                                下一页 <i class="bi bi-chevron-right"></i>
                            </span>
                            <span class="pagination-btn disabled">
                                末页 <i class="bi bi-chevron-double-right"></i>
                            </span>
                            {% endif %}
                        </div>
                    </nav>
                </div>
                {% endif %}'''
    
    # 查找旧的分页代码并替换
    # 模式1: 旧的分页结构（带fas图标）
    old_pagination_pattern = r'<!-- 分页导航.*?-->\s*<div class="pagination-wrapper">\s*<nav.*?aria-label="分页导航">.*?</nav>\s*</div>'
    
    if re.search(old_pagination_pattern, content, re.DOTALL):
        content = re.sub(old_pagination_pattern, standard_pagination, content, flags=re.DOTALL)
        print(f"✅ {description}: 已更新分页样式（旧结构）")
        return True
    else:
        # 检查是否已有新格式
        if 'statistics-info' in content and 'bi bi-chevron' in content:
            print(f"✅ {description}: 已使用新分页样式")
            return False
        else:
            print(f"⏭️  {description}: 未找到需要更新的分页代码")
            return False

def main():
    print("=" * 80)
    print("统一分页功能样式 - 批量更新工具")
    print("=" * 80)
    print()
    
    files_to_update = [
        {
            'path': r'e:\EIMS2026\eims_jiachengda\templates\eims_jiachengda\user_management.html',
            'desc': '嘉诚达 - 用户账号管理'
        },
        {
            'path': r'e:\EIMS2026\eims_app\templates\personnel\destination.html',
            'desc': '鼎策 - 人员去向'
        },
        {
            'path': r'e:\EIMS2026\eims_app\templates\personnel\certificate_list.html',
            'desc': '鼎策 - 人员证书'
        },
        {
            'path': r'e:\EIMS2026\eims_app\templates\personnel\allocation_list.html',
            'desc': '鼎策 - 人员分配'
        },
        {
            'path': r'e:\EIMS2026\eims_app\templates\contract\list.html',
            'desc': '鼎策 - 合同管理'
        },
        {
            'path': r'e:\EIMS2026\eims_app\templates\project_ledger\list.html',
            'desc': '鼎策 - 项目台账'
        },
        {
            'path': r'e:\EIMS2026\eims_jiachengda\templates\personnel\destination.html',
            'desc': '嘉诚达 - 人员去向'
        },
        {
            'path': r'e:\EIMS2026\eims_jiachengda\templates\personnel\certificate_list.html',
            'desc': '嘉诚达 - 人员证书'
        },
        {
            'path': r'e:\EIMS2026\eims_jiachengda\templates\personnel\allocation_list.html',
            'desc': '嘉诚达 - 人员分配'
        },
        {
            'path': r'e:\EIMS2026\eims_jiachengda\templates\contract\list.html',
            'desc': '嘉诚达 - 合同管理'
        },
        {
            'path': r'e:\EIMS2026\eims_jiachengda\templates\project_ledger\list.html',
            'desc': '嘉诚达 - 项目台账'
        }
    ]
    
    updated_count = 0
    already_updated = 0
    skipped = 0
    
    for file_info in files_to_update:
        result = update_pagination_style(file_info['path'], file_info['desc'])
        if result:
            updated_count += 1
        elif result is False and '已使用新分页样式' in str(result):
            already_updated += 1
        else:
            skipped += 1
        print()
    
    print("=" * 80)
    print(f"更新完成！")
    print(f"  📝 已更新: {updated_count} 个文件")
    print(f"  ✅ 已使用新样式: {already_updated} 个文件")
    print(f"  ⏭️  跳过: {skipped} 个文件")
    print("=" * 80)

if __name__ == '__main__':
    main()
