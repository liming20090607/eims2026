"""
Fix root user - assign to root admin tenant
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models.model_user import UserProfile, UserTenantRelation
from eims_app.models.model_tenant import Tenant

User = get_user_model()

print("="*80)
print("修复 root 用户 - 分配到 Root Admin 租户")
print("="*80)

# Get root user
try:
    root_user = User.objects.get(username='root')
    print(f"\n✓ 找到用户: {root_user.username}")
except User.DoesNotExist:
    print("\n✗ 用户 'root' 不存在")
    exit(1)

# Check if UserProfile exists
user_profile, created = UserProfile.objects.get_or_create(
    user=root_user,
    defaults={
        'real_name': 'Root 管理员',
        'phone': '13800138000',
    }
)

if created:
    print("✓ 创建 UserProfile")
else:
    print("✓ UserProfile 已存在")

# Check if Root Admin Tenant exists
root_tenant, created = Tenant.objects.get_or_create(
    code='root_admin',
    defaults={
        'name': 'Root Admin',
        'short_name': '超级管理员',
        'remark': '超级管理员后台'
    }
)

if created:
    print("✓ 创建 Root Admin 租户")
else:
    print("✓ Root Admin 租户已存在")

# Check if UserTenantRelation exists
relation, created = UserTenantRelation.objects.get_or_create(
    user=root_user,
    tenant=root_tenant,
    defaults={
        'is_primary': True,
        'remark': '超级管理员'
    }
)

if created:
    print("✓ 已创建 root 用户与 Root Admin 租户的关联")
else:
    print("✓ 关联已存在")

# Update UserProfile's default tenant
if user_profile.tenant != root_tenant:
    user_profile.tenant = root_tenant
    user_profile.save()
    print("✓ 已更新 UserProfile 的默认公司")
else:
    print("✓ UserProfile 默认公司已正确设置")

print("\n" + "="*80)
print("修复完成！")
print("="*80)
print(f"\n用户信息:")
print(f"  用户名: {root_user.username}")
print(f"  姓名: {user_profile.real_name}")
print(f"  是否超级管理员: {root_user.is_superuser}")
print(f"  默认公司: {user_profile.tenant.name if user_profile.tenant else '无'}")

# Get all tenant relations
relations = UserTenantRelation.objects.filter(user=root_user)
print(f"  关联的租户: {[r.tenant.name for r in relations]}")

print("\n" + "="*80)
print("现在请刷新浏览器页面并重新登录")
print("="*80)
