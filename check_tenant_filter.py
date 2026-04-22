#!/usr/bin/env python
"""
检查租户过滤问题
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_cost_sub_modules import CostProjectInfo
from eims_app.models import Tenant

print("="*60)
print("检查租户和数据分布")
print("="*60)

# 查看所有租户
print("\n所有租户:")
tenants = Tenant.objects.all()
for t in tenants:
    print(f"  ID={t.id}, 名称={t.name}, 代码={t.code}")

# 查看项目按租户分布
print("\n项目按租户分布:")
from django.db.models import Count
tenant_stats = CostProjectInfo.objects.values('tenant_id').annotate(count=Count('id')).order_by('tenant_id')
for stat in tenant_stats:
    tenant_id = stat['tenant_id']
    count = stat['count']
    if tenant_id:
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            print(f"  租户 {tenant_id} ({tenant.name}): {count} 个项目")
        except Tenant.DoesNotExist:
            print(f"  租户 {tenant_id} (不存在): {count} 个项目")
    else:
        print(f"  无租户: {count} 个项目")

# 查看ID=14的项目详情
print("\nID=14的项目详情:")
project = CostProjectInfo.objects.get(pk=14)
print(f"  项目编号: {project.project_code}")
print(f"  项目名称: {project.project_name}")
print(f"  租户ID: {project.tenant_id}")
if project.tenant_id:
    try:
        tenant = Tenant.objects.get(id=project.tenant_id)
        print(f"  租户名称: {tenant.name}")
    except:
        print(f"  租户名称: (无法获取)")

print("\n" + "="*60)
print("问题分析:")
print("="*60)
print("如果您当前登录的用户属于其他租户（不是租户4），")
print("那么租户过滤会导致您看不到这个项目。")
print("\n解决方案:")
print("1. 切换到租户4，或")
print("2. 将项目的租户改为您当前的租户")
