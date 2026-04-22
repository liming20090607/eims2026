import os
import sys
sys.path.insert(0, 'E:\\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Apply Python 3.14 compatibility patch
try:
    from django.utils import _os
    _os._safe_join = _os.safe_join
except Exception:
    pass

import django
django.setup()

from eims_app.models import Personnel, ProjectDetail
from django.db import connection

print('='*70)
print('Personnel vs ProjectDetail 模型对比')
print('='*70)

print(f'\nPersonnel 模型:')
print(f'  app_label: {Personnel._meta.app_label}')
print(f'  db_table: {Personnel._meta.db_table}')
print(f'  字段数量: {len(Personnel._meta.get_fields())}')
print(f'  has is_deleted: {hasattr(Personnel, "is_deleted")}')

# 获取 Personnel 的所有字段
personnel_field_names = [f.name for f in Personnel._meta.get_fields()]
print(f'  包含 is_deleted: {"is_deleted" in personnel_field_names}')

# 查看 Personnel 是否有外键到 ProjectDetail
for field in Personnel._meta.get_fields():
    if hasattr(field, 'related_model'):
        print(f'  外键: {field.name} -> {field.related_model._meta.model_name if field.related_model else None}')

print(f'\nProjectDetail 模型:')
print(f'  app_label: {ProjectDetail._meta.app_label}')
print(f'  db_table: {ProjectDetail._meta.db_table}')
print(f'  字段数量: {len(ProjectDetail._meta.get_fields())}')
print(f'  has is_deleted: {hasattr(ProjectDetail, "is_deleted")}')

project_field_names = [f.name for f in ProjectDetail._meta.get_fields()]
print(f'  包含 is_deleted: {"is_deleted" in project_field_names}')

# 测试 Personnel 的查询 SQL
print('\n' + '='*70)
print('测试 Personnel 查询生成的 SQL')
print('='*70)

from django.db.models import Q

# 获取 Personnel 查询的 SQL
queryset = Personnel.objects.filter(is_deleted=False)
print(f'\nPersonnel 查询:')
print(f'  Query: {str(queryset.query)}')
print(f'  Model: {queryset.model.__name__}')
print(f'  Table: {queryset.model._meta.db_table}')

# 测试不同数据库的查询
for db_alias in ['default', 'dingce', 'root_admin']:
    try:
        qs = Personnel.objects.using(db_alias).filter(is_deleted=False)
        sql = str(qs.query)
        print(f'\n  使用 {db_alias} 数据库:')
        print(f'    SQL: {sql[:200]}...')
    except Exception as e:
        print(f'\n  使用 {db_alias} 数据库失败: {e}')

print('\n' + '='*70)
print('检查是否存在模型冲突')
print('='*70)

# 检查 Django app registry 中是否有多个 Personnel 模型
from django.apps import apps

all_models = apps.get_models()
personnel_models = [m for m in all_models if m.__name__ == 'Personnel']

print(f'\nDjango 注册的 Personnel 模型数量: {len(personnel_models)}')
for i, model in enumerate(personnel_models):
    print(f'  {i+1}. {model._meta.app_label}.{model.__name__}')
    print(f'     db_table: {model._meta.db_table}')
    print(f'     fields: {len(model._meta.get_fields())}')

print('\n' + '='*70)
