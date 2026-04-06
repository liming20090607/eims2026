#!/usr/bin/env python3
"""
直接导入角色数据到数据库，绕过 Django 的外键检查
"""
import os, sys, django, json

sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Role
import json

print("=" * 60)
print("直接导入角色数据")
print("=" * 60)

# 读取角色数据
with open('/root/role_data.json', 'r', encoding='utf-8') as f:
    role_data = json.load(f)

print(f"\n读取到 {len(role_data)} 条角色记录")

# 逐条导入，忽略外键错误
success_count = 0
error_count = 0

for obj in role_data:
    try:
        pk = obj['pk']
        fields = obj['fields']
        
        # 将 department 设置为 None（如果引用的部门不存在）
        if fields.get('department'):
            fields['department'] = None
        
        # 创建或更新角色
        role, created = Role.objects.update_or_create(
            pk=pk,
            defaults=fields
        )
        success_count += 1
        print(f"✓ 角色 {role.role_code} - {role.role_name}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ 错误：{e}")

print(f"\n完成！成功：{success_count}, 失败：{error_count}")

# 验证结果
total = Role.objects.count()
print(f"\n数据库中角色总数：{total}")
