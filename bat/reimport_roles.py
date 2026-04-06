#!/usr/bin/env python3
"""
重新导入角色数据 - 修复版本
"""
import os, sys, django, json

sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Role

print("=" * 60)
print("重新导入角色数据")
print("=" * 60)

# 读取角色数据
with open('/root/role_data.json', 'r', encoding='utf-8') as f:
    role_data = json.load(f)

print(f"\n读取到 {len(role_data)} 条角色记录")

# 先清空现有数据
print("\n清空现有角色数据...")
Role.objects.all().delete()
print("已清空")

# 逐条导入
success_count = 0
error_count = 0

for obj in role_data:
    try:
        pk = obj['pk']
        fields = obj['fields']
        
        # 将 department 设置为 None（如果引用的部门不存在）
        if fields.get('department'):
            fields['department'] = None
        
        # 创建角色
        role = Role.objects.create(pk=pk, **fields)
        success_count += 1
        
        # 尝试获取角色名称用于显示
        role_name = fields.get('name', fields.get('role_name', 'N/A'))
        print(f"✓ 角色 {pk} - {role_name}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ 错误 PK={obj.get('pk')}: {e}")

print(f"\n完成！成功：{success_count}, 失败：{error_count}")

# 验证结果
total = Role.objects.count()
print(f"\n数据库中角色总数：{total}")

# 列出所有角色
print("\n角色列表:")
for role in Role.objects.all():
    print(f"  - ID: {role.id}, Name: {getattr(role, 'name', 'N/A')}")
