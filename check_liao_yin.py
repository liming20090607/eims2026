#!/usr/bin/env python
"""
检查廖志红和银雪的公司关联数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import UserTenantRelation, Employee

User = get_user_model()

print("=" * 80)
print("检查廖志红和银雪的公司关联")
print("=" * 80)

for name in ['廖志红', '银雪']:
    print(f"\n{name}:")
    users = User.objects.filter(username=name)
    
    if not users.exists():
        print(f"  未找到用户")
        continue
    
    for u in users:
        print(f"  用户ID: {u.id}")
        relations = UserTenantRelation.objects.filter(user=u).select_related('tenant')
        print(f"  公司关联数: {relations.count()}")
        
        if relations.exists():
            for r in relations:
                primary_mark = "⭐主公司" if r.is_primary else "普通公司"
                print(f"    - {r.tenant.name} ({primary_mark})")
        else:
            print(f"    无公司关联")
        
        # 检查对应的员工记录
        emps = Employee.objects.filter(name=name)
        if emps.exists():
            for emp in emps:
                print(f"  员工记录: {emp.employee_code}, tenant={emp.tenant.name if emp.tenant else 'None'}")

print("\n" + "=" * 80)
