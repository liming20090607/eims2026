"""
验证 Personnel 表数据是否完整
用于检查下拉列表数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel
from django.db import models

print('=' * 80)
print('人员下拉列表数据验证')
print('=' * 80)

# 模拟视图中的查询
personnel_names = Personnel.objects.filter(
    is_deleted=False
).order_by('name').values_list('name', flat=True).distinct()

print(f'\n下拉列表将显示 {personnel_names.count()} 人:')
print('-' * 80)

for idx, name in enumerate(personnel_names, 1):
    # 获取该人员的所有项目分配
    personnel_records = Personnel.objects.filter(
        name=name,
        is_deleted=False
    )
    
    projects = []
    for p in personnel_records:
        if p.project:
            projects.append(p.project.project_name)
    
    project_str = ', '.join(projects) if projects else '未分配项目'
    
    print(f'{idx:3d}. {name:10s} ({project_str})')

print(f'\n总计：{personnel_names.count()} 人')
print('=' * 80)

# 检查数据质量
print('\n数据质量检查:')
print('-' * 80)

# 检查空姓名
empty_names = Personnel.objects.filter(
    is_deleted=False
).filter(
    models.Q(name__isnull=True) | models.Q(name='')
).count()
print(f'空姓名记录数：{empty_names}')

# 检查单字符姓名
from django.db import models
single_char_names = Personnel.objects.filter(
    is_deleted=False
).filter(
    models.Q(name__regex=r'^[0-9a-zA-Z]$')
).count()
print(f'单字符姓名记录数：{single_char_names}')

# 检查未分配项目的人员
unassigned = Personnel.objects.filter(
    is_deleted=False,
    project__isnull=True,
    project2__isnull=True,
    project3__isnull=True,
    project4__isnull=True,
    project5__isnull=True
).count()
print(f'未分配项目人员数：{unassigned}')

print('=' * 80)
