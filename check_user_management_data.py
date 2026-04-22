#!/usr/bin/env python
"""
检查用户管理页面的数据查询逻辑
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Employee, UserTenantRelation

User = get_user_model()

print("=" * 80)
print("检查用户管理页面的数据查询")
print("=" * 80)

# 获取前5个员工
employees = Employee.objects.filter(is_deleted=False).order_by('employee_code')[:5]

for emp in employees:
    print(f"\n员工: {emp.employee_code} - {emp.name}")
    print(f"  手机号: {emp.mobile}")
    
    # 查找对应的用户（与视图逻辑相同）
    user = None
    if emp.mobile:
        user = User.objects.filter(username=emp.mobile).first()
    if not user:
        user = User.objects.filter(username=emp.name).first()
    
    if user:
        print(f"  找到用户: {user.username} (ID:{user.id})")
        
        # 查询UserTenantRelation
        relations = UserTenantRelation.objects.filter(user=user).select_related('tenant')
        if relations.exists():
            print(f"  公司关联数: {relations.count()}")
            for rel in relations:
                primary_mark = "⭐主公司" if rel.is_primary else "普通公司"
                print(f"    - {rel.tenant.name} ({primary_mark})")
        else:
            print(f"  公司关联数: 0")
    else:
        print(f"  未找到对应用户")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
