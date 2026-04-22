#!/usr/bin/env python
"""
检查各数据库中的人员数据
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from eims_app.models import Personnel, Tenant

print("=" * 70)
print("检查各数据库中的人员数据")
print("=" * 70)

# 检查各数据库
databases = ['default', 'dingce', 'shengchang', 'jiachengda']

for db_name in databases:
    print(f"\n--- 数据库: {db_name} ---")
    try:
        personnel_list = Personnel.objects.using(db_name).filter(is_deleted=False)
        count = personnel_list.count()
        print(f"  总人数: {count}")
        
        if count > 0:
            for p in personnel_list[:5]:
                print(f"  - {p.personnel_code}: {p.name} (部门: {p.department}) (tenant_id: {p.tenant_id if hasattr(p, 'tenant_id') else 'N/A'})")
            if count > 5:
                print(f"  ... 还有 {count - 5} 人")
    except Exception as e:
        print(f"  错误: {e}")

# 检查租户信息
print(f"\n--- 租户信息 (root_admin) ---")
try:
    tenants = Tenant.objects.using('root_admin').all()
    for t in tenants:
        print(f"  - {t.code}: {t.name} (ID: {t.id})")
except Exception as e:
    print(f"  错误: {e}")
