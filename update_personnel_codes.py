import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel, ProjectDetail
from django.db import transaction

print('=' * 80)
print('人员编号标准化 - 更新项目总监和现场负责人字段')
print('=' * 80)

# Step 1: Get all unique names from ProjectDetail
print('\n步骤 1: 获取 ProjectDetail 中所有唯一的人员姓名...')
directors = ProjectDetail.objects.exclude(
    project_director=''
).values_list('project_director', flat=True).distinct()

managers = ProjectDetail.objects.exclude(
    project_manager=''
).values_list('project_manager', flat=True).distinct()

all_names = set(list(directors) + list(managers))
print(f'发现 {len(all_names)} 个唯一姓名: {sorted(all_names)}')

# Step 2: Create name-to-code mapping from Personnel table
print('\n步骤 2: 从 Personnel 表创建姓名到编号的映射...')
name_to_code = {}
for p in Personnel.objects.all():
    if p.name and p.personnel_code:
        # If multiple records with same name, use the first RY code found
        if p.name not in name_to_code:
            name_to_code[p.name] = p.personnel_code
        elif p.personnel_code.startswith('RY') and len(p.personnel_code) == 5:
            # Prefer standard RY format (RY + 3 digits)
            name_to_code[p.name] = p.personnel_code

print(f'找到 {len(name_to_code)} 个姓名-编号映射')
for name, code in sorted(name_to_code.items()):
    print(f'  {name} -> {code}')

# Step 3: Check for unmapped names
print('\n步骤 3: 检查未映射的姓名...')
unmapped_names = [name for name in all_names if name not in name_to_code]
if unmapped_names:
    print(f'警告: 以下 {len(unmapped_names)} 个姓名在 Personnel 表中找不到:')
    for name in sorted(unmapped_names):
        print(f'  - {name}')
else:
    print('✓ 所有姓名都已映射')

# Step 4: Update ProjectDetail records
print('\n步骤 4: 开始更新 ProjectDetail 记录...')
updated_directors = 0
updated_managers = 0
skipped = 0

with transaction.atomic():
    for project in ProjectDetail.objects.all():
        updated = False
        
        # Update project_director
        if project.project_director and project.project_director in name_to_code:
            old_value = project.project_director
            new_code = name_to_code[project.project_director]
            if old_value != new_code:
                project.project_director = new_code
                updated = True
                updated_directors += 1
                print(f'  项目 {project.project_code}: 总监 {old_value} -> {new_code}')
        
        # Update project_manager
        if project.project_manager and project.project_manager in name_to_code:
            old_value = project.project_manager
            new_code = name_to_code[project.project_manager]
            if old_value != new_code:
                project.project_manager = new_code
                updated = True
                updated_managers += 1
                print(f'  项目 {project.project_code}: 负责人 {old_value} -> {new_code}')
        
        # Skip if no changes or unmapped names
        if not updated:
            if project.project_director and project.project_director not in name_to_code:
                print(f'  ⚠ 跳过项目 {project.project_code}: 总监 "{project.project_director}" 未找到对应编号')
                skipped += 1
            if project.project_manager and project.project_manager not in name_to_code:
                print(f'  ⚠ 跳过项目 {project.project_code}: 负责人 "{project.project_manager}" 未找到对应编号')
                skipped += 1
        
        if updated:
            project.save(update_fields=['project_director', 'project_manager'])

print('\n' + '=' * 80)
print('更新完成统计:')
print('=' * 80)
print(f'更新的总监数量: {updated_directors}')
print(f'更新的负责人数量: {updated_managers}')
print(f'跳过的记录数: {skipped}')
print(f'总处理项目数: {ProjectDetail.objects.count()}')

# Step 5: Verify results
print('\n步骤 5: 验证更新结果（抽样显示）...')
sample_projects = ProjectDetail.objects.exclude(
    project_director=''
)[:10]
print('\n更新后的项目总监字段示例:')
for proj in sample_projects:
    print(f'  项目 {proj.project_code}: 总监={proj.project_director}, 负责人={proj.project_manager}')

print('\n✓ 人员编号标准化完成！')
