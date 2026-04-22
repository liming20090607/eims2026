#!/usr/bin/env python
"""
检查银雪和廖志红的数据关联
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Employee, UserTenantRelation

User = get_user_model()

print("=" * 80)
print("检查银雪和廖志红的数据关联")
print("=" * 80)

for name in ['廖志红', '银雪']:
    print(f"\n{name}:")
    
    # 查询员工记录
    emps = Employee.objects.filter(name=name, is_deleted=False)
    if not emps.exists():
        print(f"  未找到员工记录")
        continue
    
    for emp in emps:
        print(f"  员工编号: {emp.employee_code}")
        print(f"  手机号: {emp.mobile}")
        print(f"  员工表所属公司: {emp.tenant.name if emp.tenant else 'None'}")
        
        # 视图中的用户查询逻辑
        user = None
        if emp.mobile:
            user = User.objects.filter(username=emp.mobile).first()
            print(f"  通过手机号找到用户: {user.username if user else 'None'} (ID:{user.id if user else 'N/A'})")
        if not user:
            user = User.objects.filter(username=emp.name).first()
            print(f"  通过姓名找到用户: {user.username if user else 'None'} (ID:{user.id if user else 'N/A'})")
        
        if user:
            # 查询 UserTenantRelation
            relations = UserTenantRelation.objects.filter(user=user).select_related('tenant')
            print(f"  UserTenantRelation 记录数: {relations.count()}")
            for rel in relations:
                primary_mark = "⭐主公司" if rel.is_primary else "普通公司"
                print(f"    - {rel.tenant.name} ({primary_mark})")
            
            # 检查 UserProfile
            try:
                profile_tenant = user.profile.tenant
                print(f"  UserProfile.tenant: {profile_tenant.name if profile_tenant else 'None'}")
            except Exception as e:
                print(f"  UserProfile 查询失败: {e}")

print("\n" + "=" * 80)
