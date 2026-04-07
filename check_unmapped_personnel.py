import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel, ProjectDetail

print('=' * 80)
print('检查未映射的人员和异常数据')
print('=' * 80)

# Check for dates in director/manager fields
print('\n1. 检查包含日期的异常数据...')
date_projects = ProjectDetail.objects.filter(
    project_director__regex=r'^\d{4}-\d{2}-\d{2}'
) | ProjectDetail.objects.filter(
    project_manager__regex=r'^\d{4}-\d{2}-\d{2}'
)

print(f'发现 {date_projects.count()} 个项目包含日期数据:')
for proj in date_projects:
    print(f'  项目 {proj.project_code}: 总监="{proj.project_director}", 负责人="{proj.project_manager}"')

# Check unmapped names
print('\n2. 检查 Personnel 表中缺失的人员...')
unmapped_names = ['王军', '刘雄慧', '何开华', '胡敏杰', '林桂峰']
for name in unmapped_names:
    exists = Personnel.objects.filter(name=name).exists()
    print(f'  {name}: {"✓ 存在" if exists else "✗ 不存在"}')
    if exists:
        personnel_list = Personnel.objects.filter(name=name)
        for p in personnel_list:
            print(f'    - ID={p.id}, code={p.personnel_code}')

# Check similar names (typos)
print('\n3. 检查相似姓名（可能的拼写错误）...')
similar_pairs = [
    ('黎绍昆', '黎邵昆'),
]
for name1, name2 in similar_pairs:
    count1 = Personnel.objects.filter(name=name1).count()
    count2 = Personnel.objects.filter(name=name2).count()
    proj_count1 = ProjectDetail.objects.filter(project_director=name1).count() + ProjectDetail.objects.filter(project_manager=name1).count()
    proj_count2 = ProjectDetail.objects.filter(project_director=name2).count() + ProjectDetail.objects.filter(project_manager=name2).count()
    print(f'  "{name1}": Personnel表中有{count1}条记录，项目中出现{proj_count1}次')
    print(f'  "{name2}": Personnel表中有{count2}条记录，项目中出现{proj_count2}次')

# Show all unique values that are not RY codes
print('\n4. 显示所有不是 RY 格式的人员字段值...')
non_ry_directors = ProjectDetail.objects.exclude(
    project_director=''
).exclude(
    project_director__regex=r'^RY\d{3}$'
).values_list('project_director', flat=True).distinct()

non_ry_managers = ProjectDetail.objects.exclude(
    project_manager=''
).exclude(
    project_manager__regex=r'^RY\d{3}$'
).values_list('project_manager', flat=True).distinct()

all_non_ry = set(list(non_ry_directors) + list(non_ry_managers))
print(f'发现 {len(all_non_ry)} 个非 RY 格式的值:')
for value in sorted(all_non_ry):
    print(f'  - "{value}"')
