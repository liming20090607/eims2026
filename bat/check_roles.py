#!/usr/bin/env python3
"""
导入角色数据并验证结果
"""
import os, sys, django, json

sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Role

print("=" * 60)
print("检查角色数据")
print("=" * 60)

# 查询所有角色
roles = Role.objects.all()
print(f"\n数据库中的角色数量：{len(roles)}\n")

for role in roles:
    print(f"✓ ID: {role.id}, 名称：{role.name if hasattr(role, 'name') else 'N/A'}")

print("\n完成!")
