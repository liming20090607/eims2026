"""
演示如何为用户添加多个公司关联
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import UserTenantRelation, Tenant, UserProfile

# 获取测试用户（如果没有则创建一个）
try:
    test_user = User.objects.get(username='testuser')
except User.DoesNotExist:
    test_user = User.objects.create_user(
        username='testuser',
        password='test123456#',
        first_name='测试用户'
    )
    UserProfile.objects.get_or_create(user=test_user, defaults={'real_name': '测试用户'})

# 获取所有公司
tenants = Tenant.objects.filter(is_active=True)
print(f"\n当前共有 {tenants.count()} 个公司:")
for tenant in tenants:
    print(f"  - {tenant.name} (ID: {tenant.id})")

# 为测试用户添加多个公司关联
print(f"\n为用户 '{test_user.username}' 添加多公司关联...")

for i, tenant in enumerate(tenants):
    # 第一个公司设为主公司
    is_primary = (i == 0)
    
    relation, created = UserTenantRelation.objects.get_or_create(
        user=test_user,
        tenant=tenant,
        defaults={
            'is_primary': is_primary,
            'remark': '全职' if is_primary else '兼职'
        }
    )
    
    if created:
        print(f"  ✓ 已添加: {tenant.name} ({'主公司' if is_primary else '兼职'})")
    else:
        print(f"  - 已存在: {tenant.name} (更新为主公司: {is_primary})")

# 显示用户的所有公司关联
print(f"\n用户 '{test_user.username}' 的公司关联:")
relations = UserTenantRelation.objects.filter(user=test_user).select_related('tenant')
for rel in relations:
    marker = "【主】" if rel.is_primary else ""
    print(f"  {marker} {rel.tenant.name} - {rel.remark or '无备注'}")

print(f"\n✅ 演示完成！")
print(f"\n现在可以访问:")
print(f"  后台用户列表: http://127.0.0.1:8000/admin/auth/user/")
print(f"  关联管理页面: http://127.0.0.1:8000/admin/eims_app/usertenantrelation/")
