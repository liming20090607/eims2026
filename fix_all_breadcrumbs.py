"""
修复所有公司的面包屑导航
确保每个页面都使用正确的URL命名空间（eims_app或eims_jiachengda）
"""
import os
import re

def fix_jiachengda_breadcrumbs():
    """修复嘉诚达系统的所有面包屑导航"""
    
    templates_dir = r'e:\EIMS2026\eims_jiachengda\templates'
    
    # 定义需要修复的文件和对应的面包屑结构
    breadcrumb_configs = {
        'personnel/list.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="javascript:void(0);">人证管理</a></li>
<li class="breadcrumb-item active">人员花名册</li>
{% endblock %}'''
        },
        'personnel/destination.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="javascript:void(0);">人证管理</a></li>
<li class="breadcrumb-item active">人员去向</li>
{% endblock %}'''
        },
        'personnel/certificate_list.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="javascript:void(0);">人证管理</a></li>
<li class="breadcrumb-item active">人员证书</li>
{% endblock %}'''
        },
        'personnel/allocation_list.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="javascript:void(0);">人证管理</a></li>
<li class="breadcrumb-item active">人员分配</li>
{% endblock %}'''
        },
        'contract/list.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item active">合同管理</li>
{% endblock %}'''
        },
        'contract/add.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:contract_list' %}">合同管理</a></li>
<li class="breadcrumb-item active">新增合同</li>
{% endblock %}'''
        },
        'contract/edit.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:contract_list' %}">合同管理</a></li>
<li class="breadcrumb-item active">编辑合同</li>
{% endblock %}'''
        },
        'contract/view.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:contract_list' %}">合同管理</a></li>
<li class="breadcrumb-item active">合同详情</li>
{% endblock %}'''
        },
        'project_ledger/list.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="javascript:void(0);">项目管理</a></li>
<li class="breadcrumb-item active">项目台账</li>
{% endblock %}'''
        },
        'project_ledger/detail.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:project_ledger_list' %}">项目台账</a></li>
<li class="breadcrumb-item active">项目详情</li>
{% endblock %}'''
        },
        'project_ledger/form.html': {
            'urls_to_fix': True,
            'breadcrumb': '''{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:eims_index' %}">首页</a></li>
<li class="breadcrumb-item"><a href="{% url 'eims_jiachengda:project_ledger_list' %}">项目台账</a></li>
<li class="breadcrumb-item active">项目编辑</li>
{% endblock %}'''
        },
    }
    
    total_files_fixed = 0
    total_url_replacements = 0
    
    print("=" * 80)
    print("嘉诚达系统面包屑导航修复工具")
    print("=" * 80)
    print()
    
    for filename, config in breadcrumb_configs.items():
        file_path = os.path.join(templates_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️  文件不存在: {filename}")
            continue
        
        print(f"📄 处理文件: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 修复URL命名空间 (eims_app -> eims_jiachengda)
        if config.get('urls_to_fix', False):
            # 替换所有 eims_app: 为 eims_jiachengda:
            url_count = len(re.findall(r"eims_app:", content))
            content = re.sub(r"eims_app:", "eims_jiachengda:", content)
            total_url_replacements += url_count
            print(f"  ✅ 替换 {url_count} 个URL命名空间 (eims_app → eims_jiachengda)")
        
        # 2. 替换面包屑导航块
        if 'breadcrumb' in config:
            # 查找并替换 {% block breadcrumb %} 到 {% endblock %}
            breadcrumb_pattern = r'\{% block breadcrumb %\}.*?\{% endblock %\}'
            breadcrumb_content = config['breadcrumb']
            
            if re.search(breadcrumb_pattern, content, re.DOTALL):
                content = re.sub(breadcrumb_pattern, breadcrumb_content, content, flags=re.DOTALL)
                print(f"  ✅ 更新面包屑导航")
            else:
                print(f"  ⚠️  未找到面包屑块，可能需要手动添加")
        
        # 保存修改后的内容
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            total_files_fixed += 1
            print(f"  💾 已保存修改")
        else:
            print(f"  ⏭️  无更改")
        
        print()
    
    print("=" * 80)
    print(f"修复完成！")
    print(f"  📁 修改文件数: {total_files_fixed}")
    print(f"  🔗 URL替换次数: {total_url_replacements}")
    print("=" * 80)

def verify_dingce_breadcrumbs():
    """验证鼎策系统的面包屑导航"""
    
    templates_dir = r'e:\EIMS2026\eims_app\templates'
    
    print("\n" + "=" * 80)
    print("鼎策系统面包屑导航验证")
    print("=" * 80)
    print()
    
    # 检查是否使用了正确的命名空间
    test_files = [
        'personnel/list.html',
        'personnel/destination.html',
        'contract/list.html',
        'project_ledger/list.html',
    ]
    
    for filename in test_files:
        file_path = os.path.join(templates_dir, filename)
        
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了正确的命名空间
        if 'eims_jiachengda:' in content:
            print(f"⚠️  {filename}: 发现错误的命名空间 'eims_jiachengda:'")
        else:
            print(f"✅  {filename}: 命名空间正确")

if __name__ == '__main__':
    print("\n⚠️  此操作将修改所有嘉诚达系统模板中的URL命名空间和面包屑导航")
    print("请确保已备份相关文件。\n")
    
    confirm = input("是否继续？(yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        exit(0)
    
    # 修复嘉诚达系统
    fix_jiachengda_breadcrumbs()
    
    # 验证鼎策系统
    verify_dingce_breadcrumbs()
    
    print("\n✅ 所有操作完成！")
    print("请刷新浏览器测试各页面面包屑导航功能。")
