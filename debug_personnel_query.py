#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试嘉诚达人员列表查询问题
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_personnel import Personnel
from eims_app.models.model_tenant import Tenant
from eims_app.utils.tenant_utils import filter_queryset_by_tenant

print("=" * 80)
print("  调试嘉诚达人员列表查询")
print("=" * 80)
print()

# 1. 直接查询 Personnel（不使用路由）
print("步骤 1: 直接查询嘉诚达数据库的 Personnel 表")
print("-" * 80)
all_personnel = Personnel.objects.using('jiachengda').filter(is_deleted=False)
print(f"总计: {all_personnel.count()} 条记录")

if all_personnel.exists():
    for p in all_personnel[:5]:
        print(f"  ID={p.id}, code={p.personnel_code}, name={p.name}, tenant_id={p.tenant_id}, is_deleted={p.is_deleted}")
else:
    print("✗ 没有数据")

print()

# 2. 使用数据库路由模拟查询
print("步骤 2: 模拟数据库路由查询（不传 request）")
print("-" * 80)
personnel_no_request = Personnel.objects.filter(is_deleted=False).order_by('personnel_code')
print(f"查询使用的数据库: {personnel_no_request.db}")
print(f"总计: {personnel_no_request.count()} 条记录")

if personnel_no_request.exists():
    for p in personnel_no_request[:5]:
        print(f"  ID={p.id}, code={p.personnel_code}, name={p.name}, tenant_id={p.tenant_id}")
else:
    print("✗ 没有数据")

print()

# 3. 模拟带有 request.tenant 的查询
print("步骤 3: 模拟带有 request.tenant 的查询")
print("-" * 80)

# 获取嘉诚达租户
try:
    jiachengda_tenant = Tenant.objects.get(code='jiachengda')
    print(f"嘉诚达租户: ID={jiachengda_tenant.id}, code={jiachengda_tenant.code}")
    
    # 创建模拟 request 对象
    class MockRequest:
        pass
    
    mock_request = MockRequest()
    mock_request.tenant = jiachengda_tenant
    mock_request.current_system = 'jiachengda'
    
    # 基础查询
    base_query = Personnel.objects.filter(is_deleted=False).order_by('personnel_code')
    print(f"基础查询使用的数据库: {base_query.db}")
    print(f"基础查询结果数: {base_query.count()}")
    
    # 应用租户过滤
    filtered_query = filter_queryset_by_tenant(base_query, mock_request)
    print(f"\n应用租户过滤后:")
    print(f"过滤后的 SQL: {filtered_query.query}")
    print(f"过滤后的结果数: {filtered_query.count()}")
    
    if filtered_query.exists():
        print("\n过滤后的前5条记录:")
        for p in filtered_query[:5]:
            print(f"  ID={p.id}, code={p.personnel_code}, name={p.name}, tenant_id={p.tenant_id}")
    else:
        print("✗ 过滤后没有数据")
        
except Tenant.DoesNotExist:
    print("✗ 找不到嘉诚达租户")

print()
print("=" * 80)
print("  分析")
print("=" * 80)
print("""
可能的原因：
1. 数据库路由没有正确识别 'jiachengda' 系统
2. Session 中没有设置 tenant_id
3. filter_queryset_by_tenant 函数没有正确应用过滤
4. Personnel 记录的 tenant_id 与实际租户 ID 不匹配

建议检查：
- 用户登录后是否选择了"嘉诚达"公司
- Session 中的 tenant_id 是否为 4
- 浏览器是否清除了缓存和 Cookie
""")
