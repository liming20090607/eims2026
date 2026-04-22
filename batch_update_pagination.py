#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量更新分页样式的脚本
将旧的分页格式统一更新为新的标准化格式
"""

import os
import re

# 需要更新的文件列表
files_to_update = [
    'eims_app/templates/department/approval_chain_list.html',
    'eims_app/templates/archive_management/approval_chain_list.html',
    'eims_app/templates/workflow/flow_list.html',
    'eims_app/templates/contract_management/approval_chain_list.html',
    'eims_app/templates/seal_management/approval_chain_list.html',
    'eims_app/templates/cost_contract_management/list.html',
    'eims_app/templates/personnel/allocation_list.html',
]

# 旧的pagination模式（Bootstrap pagination组件）
old_pagination_pattern = r'''            <!-- 分页 -->
            \{% if page_obj\.has_other_pages %\}
            <nav aria-label="Page navigation">
                <ul class="pagination justify-content-center mb-0">
                    \{% if page_obj\.has_previous %\}
                    <li class="page-item">
                        <a class="page-link" href="\?page=1([^"]*)">首页</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="\?page=\{\{ page_obj\.previous_page_number \}\}([^"]*)">上一页</a>
                    </li>
                    \{% endif %\}

                    <li class="page-item active">
                        <span class="page-link">第 \{\{ page_obj\.number \}\} / \{\{ page_obj\.paginator\.num_pages \}\} 页</span>
                    </li>

                    \{% if page_obj\.has_next %\}
                    <li class="page-item">
                        <a class="page-link" href="\?page=\{\{ page_obj\.next_page_number \}\}([^"]*)">下一页</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="\?page=\{\{ page_obj\.paginator\.num_pages \}\}([^"]*)">末页</a>
                    </li>
                    \{% endif %\}
                </ul>
            </nav>
            \{% endif %\}'''

# 新的pagination模板
new_pagination_template = '''            <!-- 分页导航 -->
            {{% if page_obj.paginator.num_pages > 1 or page_obj.number == 1 %}}
            <div class="pagination-wrapper" style="flex-shrink: 0; background: #f8f9fc; border-top: 1px solid #e3e6f0; padding: 0.4rem 0; box-shadow: none; position: relative; z-index: 10; margin-top: 0; width: 100%;">
                <nav aria-label="分页导航">
                    <div class="pagination-container">
                        <!-- 统计信息 - 靠左 -->
                        <div class="statistics-info" style="position: absolute; left: 1rem; white-space: nowrap;">
                            <span>总记录数: <strong class="text-primary">{{{{ page_obj.paginator.count }}}}</strong> 条</span>
                            <span class="ms-2">当前页: <strong class="text-success">{{{{ page_obj.number }}}}</strong> / {{{{ page_obj.paginator.num_pages }}}}</span>
                            <span class="ms-2">本页: <strong class="text-info">{{{{ page_obj|length }}}}</strong> 条</span>
                        </div>
                        
                        <!-- 分页导航 - 居中 -->
                        {{% if page_obj.has_previous %}}
                        <a href="?page=1{{{{ params_suffix }}}}" class="pagination-btn">
                            <i class="bi bi-chevron-double-left"></i> 首页
                        </a>
                        <a href="?page={{{{ page_obj.previous_page_number }}}}{{{{ params_suffix }}}}" class="pagination-btn">
                            <i class="bi bi-chevron-left"></i> 上一页
                        </a>
                        {{% else %}}
                        <span class="pagination-btn disabled">
                            <i class="bi bi-chevron-double-left"></i> 首页
                        </span>
                        <span class="pagination-btn disabled">
                            <i class="bi bi-chevron-left"></i> 上一页
                        </span>
                        {{% endif %}}
                        
                        <span class="pagination-info">
                            第 {{{{ page_obj.number }}}} / {{{{ page_obj.paginator.num_pages }}}} 页
                        </span>
                        
                        {{% if page_obj.has_next %}}
                        <a href="?page={{{{ page_obj.next_page_number }}}}{{{{ params_suffix }}}}" class="pagination-btn">
                            下一页 <i class="bi bi-chevron-right"></i>
                        </a>
                        <a href="?page={{{{ page_obj.paginator.num_pages }}}}{{{{ params_suffix }}}}" class="pagination-btn">
                            末页 <i class="bi bi-chevron-double-right"></i>
                        </a>
                        {{% else %}}
                        <span class="pagination-btn disabled">
                            下一页 <i class="bi bi-chevron-right"></i>
                        </span>
                        <span class="pagination-btn disabled">
                            末页 <i class="bi bi-chevron-double-right"></i>
                        </span>
                        {{% endif %}}
                    </div>
                </nav>
            </div>
            {{% endif %}}'''

# CSS样式模板
css_template = '''
{% block extra_css %}
<style>
    /* 分页导航样式 */
    .pagination-wrapper {
        flex-shrink: 0;
        background: #f8f9fc;
        border-top: 1px solid #e3e6f0;
        padding: 0.4rem 0;
        box-shadow: none;
        position: relative;
        z-index: 10;
        margin-top: 0;
        width: 100%;
    }
    
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.3rem;
        width: 100%;
        position: relative;
    }
    
    /* 统计信息样式 */
    .statistics-info {
        font-size: 0.85rem;
        color: #6c757d;
    }
    
    .statistics-info strong {
        font-weight: 600;
    }
    
    .pagination-btn {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        font-size: 0.8rem;
        color: #4e73df;
        background: white;
        border: 1px solid #d1d3e2;
        border-radius: 0.25rem;
        text-decoration: none;
        line-height: 1.2;
        transition: all 0.2s ease;
    }
    
    .pagination-btn:hover {
        background: #4e73df;
        color: white;
        border-color: #4e73df;
        text-decoration: none;
    }
    
    .pagination-btn.disabled {
        color: #6c757d;
        background: #e9ecef;
        border-color: #d1d3e2;
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .pagination-info {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
        background: #4e73df;
        border: 1px solid #4e73df;
        border-radius: 0.25rem;
        line-height: 1.2;
    }
</style>
{% endblock %}
'''

def update_file(file_path):
    """更新单个文件的分页样式"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 检查是否已经有extra_css块
    if '{% block extra_css %}' not in content:
        # 在title block后添加CSS
        title_pattern = r'({% block title %}.*?{% endblock %})'
        match = re.search(title_pattern, content, re.DOTALL)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + '\n' + css_template + content[insert_pos:]
            print(f"✓ 已添加CSS样式到: {file_path}")
    
    # 替换旧的分页HTML
    # 由于正则表达式复杂,使用更简单的方法
    if '{% if page_obj.has_other_pages %}' in content and '<ul class="pagination' in content:
        # 找到并替换整个pagination部分
        lines = content.split('\n')
        new_lines = []
        skip_until_endif = False
        in_old_pagination = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检测旧的分页开始
            if '<!-- 分页 -->' in line and i + 1 < len(lines) and '{% if page_obj.has_other_pages %}' in lines[i+1]:
                in_old_pagination = True
                skip_until_endif = False
                # 添加新的分页代码
                new_lines.append('            <!-- 分页导航 -->')
                new_lines.append('            {% if page_obj.paginator.num_pages > 1 or page_obj.number == 1 %}')
                new_lines.append('            <div class="pagination-wrapper" style="flex-shrink: 0; background: #f8f9fc; border-top: 1px solid #e3e6f0; padding: 0.4rem 0; box-shadow: none; position: relative; z-index: 10; margin-top: 0; width: 100%;">')
                new_lines.append('                <nav aria-label="分页导航">')
                new_lines.append('                    <div class="pagination-container">')
                new_lines.append('                        <!-- 统计信息 - 靠左 -->')
                new_lines.append('                        <div class="statistics-info" style="position: absolute; left: 1rem; white-space: nowrap;">')
                new_lines.append('                            <span>总记录数: <strong class="text-primary">{{ page_obj.paginator.count }}</strong> 条</span>')
                new_lines.append('                            <span class="ms-2">当前页: <strong class="text-success">{{ page_obj.number }}</strong> / {{ page_obj.paginator.num_pages }}</span>')
                new_lines.append('                            <span class="ms-2">本页: <strong class="text-info">{{ page_obj|length }}</strong> 条</span>')
                new_lines.append('                        </div>')
                new_lines.append('                        ')
                new_lines.append('                        <!-- 分页导航 - 居中 -->')
                new_lines.append('                        {% if page_obj.has_previous %}')
                new_lines.append('                        <a href="?page=1" class="pagination-btn">')
                new_lines.append('                            <i class="bi bi-chevron-double-left"></i> 首页')
                new_lines.append('                        </a>')
                new_lines.append('                        <a href="?page={{ page_obj.previous_page_number }}" class="pagination-btn">')
                new_lines.append('                            <i class="bi bi-chevron-left"></i> 上一页')
                new_lines.append('                        </a>')
                new_lines.append('                        {% else %}')
                new_lines.append('                        <span class="pagination-btn disabled">')
                new_lines.append('                            <i class="bi bi-chevron-double-left"></i> 首页')
                new_lines.append('                        </span>')
                new_lines.append('                        <span class="pagination-btn disabled">')
                new_lines.append('                            <i class="bi bi-chevron-left"></i> 上一页')
                new_lines.append('                        </span>')
                new_lines.append('                        {% endif %}')
                new_lines.append('                        ')
                new_lines.append('                        <span class="pagination-info">')
                new_lines.append('                            第 {{ page_obj.number }} / {{ page_obj.paginator.num_pages }} 页')
                new_lines.append('                        </span>')
                new_lines.append('                        ')
                new_lines.append('                        {% if page_obj.has_next %}')
                new_lines.append('                        <a href="?page={{ page_obj.next_page_number }}" class="pagination-btn">')
                new_lines.append('                            下一页 <i class="bi bi-chevron-right"></i>')
                new_lines.append('                        </a>')
                new_lines.append('                        <a href="?page={{ page_obj.paginator.num_pages }}" class="pagination-btn">')
                new_lines.append('                            末页 <i class="bi bi-chevron-double-right"></i>')
                new_lines.append('                        </a>')
                new_lines.append('                        {% else %}')
                new_lines.append('                        <span class="pagination-btn disabled">')
                new_lines.append('                            下一页 <i class="bi bi-chevron-right"></i>')
                new_lines.append('                        </span>')
                new_lines.append('                        <span class="pagination-btn disabled">')
                new_lines.append('                            末页 <i class="bi bi-chevron-double-right"></i>')
                new_lines.append('                        </span>')
                new_lines.append('                        {% endif %}')
                new_lines.append('                    </div>')
                new_lines.append('                </nav>')
                new_lines.append('            </div>')
                new_lines.append('            {% endif %}')
                i += 1  # 跳过 <!-- 分页 -->
                continue
            
            # 如果在旧的分页块中,跳过直到遇到对应的{% endif %}
            if in_old_pagination:
                if '{% endif %}' in line and not skip_until_endif:
                    # 这是第一个endif,继续跳过
                    skip_until_endif = True
                    i += 1
                    continue
                elif '</nav>' in line or '</ul>' in line:
                    # 结束标记,下一个应该是endif
                    i += 1
                    continue
                elif skip_until_endif and '{% endif %}' in line:
                    # 真正的结束
                    in_old_pagination = False
                    skip_until_endif = False
                    i += 1
                    continue
                else:
                    # 跳过这一行
                    i += 1
                    continue
            
            new_lines.append(line)
            i += 1
        
        content = '\n'.join(new_lines)
        print(f"✓ 已更新分页结构: {file_path}")
    
    # 写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"- 无需更新: {file_path}")
        return False

def main():
    """主函数"""
    print("开始批量更新分页样式...\n")
    
    updated_count = 0
    for file_path in files_to_update:
        full_path = os.path.join('e:\\EIMS2026', file_path)
        if update_file(full_path):
            updated_count += 1
    
    print(f"\n完成! 共更新了 {updated_count}/{len(files_to_update)} 个文件")

if __name__ == '__main__':
    main()
