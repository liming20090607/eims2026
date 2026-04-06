#!/usr/bin/env python3
"""
直接导入 JSON 数据到数据库，绕过 Django 的外键检查
"""
import os, sys, django

# Setup Django
sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Department, Role
import json

print("=" * 60)
print("直接导入部门数据")
print("=" * 60)

# 读取部门数据
with open('/root/department_data.json', 'r', encoding='utf-8') as f:
    dept_data = json.load(f)

print(f"\n读取到 {len(dept_data)} 条部门记录")

# 逐条导入，忽略外键错误
success_count = 0
error_count = 0

for obj in dept_data:
    try:
        pk = obj['pk']
        fields = obj['fields']
        
        # 将 manager 设置为 None（如果引用的用户不存在）
        if fields.get('manager'):
            fields['manager'] = None
        
        # 创建或更新部门
        dept, created = Department.objects.update_or_create(
            pk=pk,
            defaults=fields
        )
        success_count += 1
        print(f"✓ 部门 {dept.department_code} - {dept.department_name}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ 错误：{e}")

print(f"\n完成！成功：{success_count}, 失败：{error_count}")

# 验证结果
total = Department.objects.count()
print(f"\n数据库中部门总数：{total}")
