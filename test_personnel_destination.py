#!/usr/bin/env python
"""
测试 personnel_destination 视图是否能正常工作
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from eims_app.models import Personnel, ProjectDetail, Tenant
from django.test import RequestFactory

print("=" * 70)
print("测试 personnel_destination 视图功能")
print("=" * 70)

# 测试1: 检查 Personnel 和 ProjectDetail 模型
print("\n测试1: 模型检查")
print(f"  Personnel 有 is_deleted: {hasattr(Personnel, 'is_deleted')}")
print(f"  ProjectDetail 有 is_deleted: {hasattr(ProjectDetail, 'is_deleted')}")

# 测试2: Personnel 查询（带 is_deleted 过滤）
print("\n测试2: Personnel 查询")
try:
    personnel_list = list(Personnel.objects.filter(is_deleted=False)[:10])
    print(f"  ✓ 成功查询 {len(personnel_list)} 条 Personnel 记录")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: ProjectDetail 查询（不带 is_deleted 过滤）
print("\n测试3: ProjectDetail 查询（不带is_deleted）")
try:
    project_list = list(ProjectDetail.objects.all()[:10])
    print(f"  ✓ 成功查询 {len(project_list)} 条 ProjectDetail 记录")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 模拟 request 对象，测试视图逻辑
print("\n测试4: 模拟视图逻辑")
try:
    from eims_app.views.views_personnel import personnel_destination
    from django.contrib.auth.models import User
    
    # 创建一个测试用户
    test_user, _ = User.objects.get_or_create(username='test_user')
    
    # 创建 RequestFactory 实例
    factory = RequestFactory()
    request = factory.get('/root/personnel/destination/')
    request.user = test_user
    request.tenant = None  # /root/ 路径可能没有 tenant
    request.current_system = 'root'
    
    # 尝试获取视图函数
    print(f"  视图函数: {personnel_destination.__name__}")
    print(f"  ✓ 视图函数存在")
    
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试5: 检查数据库中的 Tenant 数据
print("\n测试5: Tenant 数据检查")
try:
    tenants = Tenant.objects.using('root_admin').all()
    print(f"  ✓ 找到 {tenants.count()} 个租户:")
    for tenant in tenants:
        print(f"    - {tenant.name} (code: {tenant.code})")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 测试6: 检查 Personnel 在各数据库的分布
print("\n测试6: Personnel 数据库分布")
for db_alias in ['default', 'dingce', 'shengchang', 'jiachengda']:
    try:
        count = Personnel.objects.using(db_alias).filter(is_deleted=False).count()
        print(f"  ✓ {db_alias}: {count} 条记录")
    except Exception as e:
        print(f"  ✗ {db_alias}: {e}")

print("\n" + "=" * 70)
print("测试完成！请在浏览器中访问 http://127.0.0.1:8000/root/personnel/destination/")
print("确认页面是否正常显示")
print("=" * 70)
