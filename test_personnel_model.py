import os
import sys

# Add project root to path
sys.path.insert(0, 'E:\\EIMS2026')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Apply Python 3.14 compatibility patch before importing Django
try:
    from django.utils import _os
    _os._safe_join = _os.safe_join
except Exception:
    pass

import django
django.setup()

from eims_app.models.model_personnel import Personnel
from eims_app.models.model_project_detail import ProjectDetail

print('='*70)
print('测试 Personnel 模型字段')
print('='*70)

# 检查 Personnel 模型的字段
personnel_fields = [f.name for f in Personnel._meta.get_fields()]
print(f'\nPersonnel 字段数量: {len(personnel_fields)}')
print(f'Personnel 字段列表: {", ".join(personnel_fields)}')

if 'is_deleted' in personnel_fields:
    print('✓ Personnel 模型有 is_deleted 字段')
else:
    print('✗ Personnel 模型缺少 is_deleted 字段！')

# 检查 ProjectDetail 模型的字段
project_fields = [f.name for f in ProjectDetail._meta.get_fields()]
print(f'\nProjectDetail 字段数量: {len(project_fields)}')
print(f'ProjectDetail 字段列表: {", ".join(project_fields)}')

if 'is_deleted' in project_fields:
    print('✓ ProjectDetail 模型有 is_deleted 字段')
else:
    print('✗ ProjectDetail 模型缺少 is_deleted 字段！')

# 测试 Personnel 查询
print('\n' + '='*70)
print('测试 Personnel 查询（使用 root_admin 数据库）')
print('='*70)

try:
    # 使用 root_admin 数据库测试
    count = Personnel.objects.using('root_admin').filter(is_deleted=False).count()
    print(f'✓ Personnel 在 root_admin 中有 {count} 条记录')
except Exception as e:
    print(f'✗ Personnel 查询 root_admin 失败: {e}')

try:
    # 使用 dingce 数据库测试
    count = Personnel.objects.using('dingce').filter(is_deleted=False).count()
    print(f'✓ Personnel 在 dingce 中有 {count} 条记录')
except Exception as e:
    print(f'✗ Personnel 查询 dingce 失败: {e}')

print('\n' + '='*70)
