#!/usr/bin/env python
"""
测试Personnel查询问题
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from eims_app.models import Personnel, ProjectDetail

print("=" * 70)
print("测试 Personnel 查询")
print("=" * 70)

# 测试1: 直接查询
print("\n测试1: Personnel.objects.filter(is_deleted=False)")
try:
    count = Personnel.objects.filter(is_deleted=False).count()
    print(f"  ✓ 成功: {count} 条记录")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 使用 using('default')
print("\n测试2: Personnel.objects.using('default').filter(is_deleted=False)")
try:
    count = Personnel.objects.using('default').filter(is_deleted=False).count()
    print(f"  ✓ 成功: {count} 条记录")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 使用 using('dingce')
print("\n测试3: Personnel.objects.using('dingce').filter(is_deleted=False)")
try:
    count = Personnel.objects.using('dingce').filter(is_deleted=False).count()
    print(f"  ✓ 成功: {count} 条记录")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 检查ProjectDetail是否有is_deleted
print("\n测试4: ProjectDetail 模型检查")
print(f"  ProjectDetail 有 is_deleted: {hasattr(ProjectDetail, 'is_deleted')}")
try:
    count = ProjectDetail.objects.using('default').all().count()
    print(f"  ✓ ProjectDetail查询成功: {count} 条记录")
except Exception as e:
    print(f"  ✗ ProjectDetail查询失败: {e}")

# 测试5: 检查模型字段
print("\n测试5: Personnel 字段列表")
personnel_fields = [f.name for f in Personnel._meta.get_fields()]
print(f"  总字段数: {len(personnel_fields)}")
print(f"  包含 is_deleted: {'is_deleted' in personnel_fields}")
if 'is_deleted' in personnel_fields:
    field = Personnel._meta.get_field('is_deleted')
    print(f"  is_deleted 字段类型: {field.__class__.__name__}")
    print(f"  is_deleted 默认值: {field.default}")

print("\n测试6: ProjectDetail 字段列表")
project_fields = [f.name for f in ProjectDetail._meta.get_fields()]
print(f"  总字段数: {len(project_fields)}")
print(f"  包含 is_deleted: {'is_deleted' in project_fields}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
