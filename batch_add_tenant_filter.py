"""
批量为视图添加租户过滤的脚本
"""
import os
import re

# 定义需要修改的视图文件及其对应的模型
VIEWS_TO_UPDATE = [
    ('eims_app/views/views_personnel.py', 'Personnel'),
    ('eims_app/views/views_notice.py', 'Notice'),
    ('eims_app/views/views_file_manage.py', 'FileManage'),
    ('eims_app/views/views_department.py', 'Department'),
    ('eims_app/views/views_personnel_detail.py', None),  # 多个模型
    ('eims_app/views/views_seal_approval.py', 'SealApproval'),
]

def add_tenant_filter_to_view(file_path, model_name=None):
    """
    为视图文件添加租户过滤
    """
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入了 tenant_utils
    if 'from ..utils.tenant_utils import' in content or 'from eims_app.utils.tenant_utils import' in content:
        print(f"⏭️  已导入 tenant_utils: {file_path}")
        return True
    
    # 查找导入语句的位置（在最后一个 from .. 或 from eims_app 之后）
    import_pattern = r'(from \.\.models import .*\n|from eims_app\.models import .*\n)'
    match = re.search(import_pattern, content)
    
    if not match:
        print(f"⚠️  未找到合适的导入位置: {file_path}")
        return False
    
    # 添加导入语句
    insert_pos = match.end()
    new_import = "from ..utils.tenant_utils import filter_queryset_by_tenant\n"
    
    # 检查相对路径
    if 'from eims_app' in content[:insert_pos]:
        new_import = "from eims_app.utils.tenant_utils import filter_queryset_by_tenant\n"
    
    content = content[:insert_pos] + new_import + content[insert_pos:]
    
    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已添加导入: {file_path}")
    return True


if __name__ == '__main__':
    print("="*60)
    print("批量为视图添加租户过滤导入")
    print("="*60)
    print()
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    for view_file, model in VIEWS_TO_UPDATE:
        file_path = os.path.join(project_root, view_file)
        add_tenant_filter_to_view(file_path, model)
    
    print()
    print("="*60)
    print("完成！请手动修改各个列表函数使用 filter_queryset_by_tenant")
    print("="*60)
