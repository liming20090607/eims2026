#!/usr/bin/env python
"""
检查Personnel模型的数据库表映射
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from eims_app.models import Personnel, ProjectDetail

print("=" * 60)
print("Personnel 模型信息")
print("=" * 60)
print(f"模型名称: {Personnel.__name__}")
print(f"应用标签: {Personnel._meta.app_label}")
print(f"数据库表名: {Personnel._meta.db_table}")
print(f"字段列表:")
for field in Personnel._meta.get_fields():
    print(f"  - {field.name} ({field.__class__.__name__})")

print("\n" + "=" * 60)
print("ProjectDetail 模型信息")
print("=" * 60)
print(f"模型名称: {ProjectDetail.__name__}")
print(f"应用标签: {ProjectDetail._meta.app_label}")
print(f"数据库表名: {ProjectDetail._meta.db_table}")
print(f"是否有 is_deleted 字段: {hasattr(ProjectDetail, 'is_deleted')}")
print(f"字段列表:")
for field in ProjectDetail._meta.get_fields():
    print(f"  - {field.name} ({field.__class__.__name__})")

# 测试查询
print("\n" + "=" * 60)
print("测试查询")
print("=" * 60)

try:
    print("测试 Personnel.objects.using('default').filter(is_deleted=False)")
    count = Personnel.objects.using('default').filter(is_deleted=False).count()
    print(f"结果: {count} 条记录")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n测试 ProjectDetail.objects.using('default').all()")
    count = ProjectDetail.objects.using('default').all().count()
    print(f"结果: {count} 条记录")
except Exception as e:
    print(f"错误: {e}")
