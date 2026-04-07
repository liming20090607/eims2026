import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel, ProjectDetail
from django.db import transaction
from datetime import datetime

print('=' * 80)
print('人员编号标准化 - 补充缺失人员和修复异常数据')
print('=' * 80)

# Step 1: Add missing personnel with RY codes
print('\n步骤 1: 为缺失的人员创建 Personnel 记录...')
missing_personnel = [
    ('王军', None),
    ('刘雄慧', None),
    ('何开华', None),
    ('胡敏杰', None),
    ('林桂峰', None),
]

# Find the highest RY number to continue sequence
existing_codes = Personnel.objects.filter(
    personnel_code__regex=r'^RY\d{3}$'
).values_list('personnel_code', flat=True)

max_num = 0
for code in existing_codes:
    try:
        num = int(code[2:])  # Extract number after "RY"
        max_num = max(max_num, num)
    except:
        pass

print(f'当前最大 RY 编号: RY{max_num:03d}')

created_personnel = []
for name, existing_code in missing_personnel:
    if not Personnel.objects.filter(name=name).exists():
        max_num += 1
        new_code = f'RY{max_num:03d}'
        personnel = Personnel.objects.create(
            personnel_code=new_code,
            name=name,
            gender=0,  # Default to male
        )
        created_personnel.append((name, new_code))
        print(f'  ✓ 创建: {name} -> {new_code}')
    else:
        p = Personnel.objects.filter(name=name).first()
        print(f'  ⊙ 已存在: {name} -> {p.personnel_code}')

# Step 2: Fix typo "黎邵昆" -> "黎绍昆"
print('\n步骤 2: 修复姓名拼写错误...')
typo_fixes = [
    ('黎邵昆', '黎绍昆'),  # Should be 黎绍昆
]

for wrong_name, correct_name in typo_fixes:
    # Get the correct code
    correct_personnel = Personnel.objects.filter(name=correct_name).first()
    if correct_personnel:
        correct_code = correct_personnel.personnel_code
        # Update ProjectDetail records
        updated_count = ProjectDetail.objects.filter(project_director=wrong_name).update(
            project_director=correct_code
        ) + ProjectDetail.objects.filter(project_manager=wrong_name).update(
            project_manager=correct_code
        )
        print(f'  ✓ 修复 "{wrong_name}" -> "{correct_name}" ({correct_code}), 更新 {updated_count} 条记录')
    else:
        print(f'  ⚠ 警告: 找不到正确姓名 "{correct_name}" 的记录')

# Step 3: Clear date values and other abnormal data
print('\n步骤 3: 清理异常数据（日期、数字等）...')
abnormal_values = [
    '2022-06-01 00:00:00',
    '2022-08-31 00:00:00',
    '2022-11-19 00:00:00',
    '2023-06-06 00:00:00',
    '2023-12-13 00:00:00',
    '2024-01-20 00:00:00',
    '2027/3/17',
    '5',
    '已解锁',
    '张振',
    '王敏志，张中立',
]

cleared_count = 0
with transaction.atomic():
    for value in abnormal_values:
        # Clear from project_director
        count1 = ProjectDetail.objects.filter(project_director=value).update(
            project_director=''
        )
        # Clear from project_manager
        count2 = ProjectDetail.objects.filter(project_manager=value).update(
            project_manager=''
        )
        if count1 or count2:
            cleared_count += count1 + count2
            print(f'  ✓ 清理 "{value}": {count1 + count2} 条记录')

print(f'  总计清理 {cleared_count} 条异常记录')

# Step 4: Re-run the main update for newly added personnel
print('\n步骤 4: 重新运行主更新脚本以包含新添加的人员...')

# Build complete name-to-code mapping
name_to_code = {}
for p in Personnel.objects.all():
    if p.name and p.personnel_code:
        if p.name not in name_to_code:
            name_to_code[p.name] = p.personnel_code
        elif p.personnel_code.startswith('RY') and len(p.personnel_code) == 5:
            name_to_code[p.name] = p.personnel_code

print(f'  映射表包含 {len(name_to_code)} 个姓名')

updated_count = 0
with transaction.atomic():
    for project in ProjectDetail.objects.all():
        updated = False
        
        # Update project_director if it's still a name
        if project.project_director and project.project_director in name_to_code:
            old_value = project.project_director
            new_code = name_to_code[project.project_director]
            if old_value != new_code:
                project.project_director = new_code
                updated = True
        
        # Update project_manager if it's still a name
        if project.project_manager and project.project_manager in name_to_code:
            old_value = project.project_manager
            new_code = name_to_code[project.project_manager]
            if old_value != new_code:
                project.project_manager = new_code
                updated = True
        
        if updated:
            project.save(update_fields=['project_director', 'project_manager'])
            updated_count += 1

print(f'  ✓ 更新了 {updated_count} 个项目记录')

# Step 5: Final verification
print('\n步骤 5: 最终验证...')
total_projects = ProjectDetail.objects.count()
projects_with_ry_director = ProjectDetail.objects.filter(
    project_director__regex=r'^RY\d{3}$'
).count()
projects_with_ry_manager = ProjectDetail.objects.filter(
    project_manager__regex=r'^RY\d{3}$'
).count()
projects_with_non_ry = total_projects - projects_with_ry_director

print(f'\n总项目数: {total_projects}')
print(f'总监字段为 RY 格式: {projects_with_ry_director}')
print(f'负责人字段为 RY 格式: {projects_with_ry_manager}')
print(f'总监字段非 RY 格式: {projects_with_non_ry}')

if projects_with_non_ry > 0:
    print('\n剩余非 RY 格式的总监值:')
    non_ry = ProjectDetail.objects.exclude(
        project_director=''
    ).exclude(
        project_director__regex=r'^RY\d{3}$'
    ).values_list('project_director', flat=True).distinct()
    for val in non_ry:
        count = ProjectDetail.objects.filter(project_director=val).count()
        print(f'  - "{val}" ({count} 个项目)')

print('\n✓ 人员编号标准化全部完成！')
print('=' * 80)
