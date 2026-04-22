"""修复陈连华的用户租户分配问题"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import UserProfile, Tenant, Personnel

print("="*80)
print("诊断用户租户分配问题")
print("="*80)

# 查找陈连华的用户
users = User.objects.filter(first_name='陈连华') | User.objects.filter(last_name='陈连华')
if not users.exists():
    users = User.objects.filter(username__icontains='chen')

print(f"\n找到 {users.count()} 个匹配用户:")
for user in users:
    print(f"  - ID:{user.id} 用户名:{user.username} 姓名:{user.get_full_name()}")

if users.exists():
    user = users.first()
    
    # 检查UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    print(f"\nUserProfile: {profile}")
    print(f"  当前租户: {profile.tenant}")
    
    # 查找陈连华的人员记录
    personnel = Personnel.objects.filter(name='陈连华').first()
    if personnel:
        print(f"\n人员记录: {personnel}")
        print(f"  部门: {personnel.department}")
        print(f"  租户ID: {personnel.tenant_id}")
        
        # 如果人员记录有租户，但UserProfile没有，就同步
        if personnel.tenant_id and not profile.tenant_id:
            tenant = Tenant.objects.get(id=personnel.tenant_id)
            profile.tenant = tenant
            profile.save(update_fields=['tenant'])
            print(f"\n✓ 已同步租户: {tenant.name}")
        elif not profile.tenant_id:
            # 获取所有活跃租户
            tenants = Tenant.objects.filter(is_active=True)
            print(f"\n可用租户 ({tenants.count()}个):")
            for t in tenants:
                print(f"  - ID:{t.id} 名称:{t.name} 代码:{t.code}")
            
            # 默认使用嘉诚达
            jiachengda = Tenant.objects.filter(code='jiachengda').first()
            if jiachengda:
                profile.tenant = jiachengda
                profile.save(update_fields=['tenant'])
                print(f"\n✓ 已分配默认租户: {jiachengda.name}")
    else:
        print("\n⚠ 未找到陈连华的人员记录")

print("\n" + "="*80)
print("诊断完成")
print("="*80)
