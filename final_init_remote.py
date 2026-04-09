import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== 数据库状态检查 ===\n")

# 检查 Tenant 表
tenant_count = Tenant.objects.count()
print(f"Tenant 表记录数: {tenant_count}")
if tenant_count == 0:
    print("正在创建默认公司...")
    tenant = Tenant.objects.create(
        name='协同AI办公系统',
        code='XTCOAI',
        is_active=True,
        remark='默认公司'
    )
    print(f"✓ 已创建公司: {tenant.name}")
else:
    for t in Tenant.objects.all():
        print(f"  - {t.name} (code: {t.code}, active: {t.is_active})")
    tenant = Tenant.objects.first()

# 检查超级管理员关联
admin_user = User.objects.filter(is_superuser=True).first()
if admin_user:
    print(f"\n超级管理员: {admin_user.username}")
    try:
        profile = admin_user.profile
        print(f"  UserProfile 存在, tenant: {profile.tenant}")
        if profile.tenant != tenant:
            profile.tenant = tenant
            profile.save()
            print(f"  ✓ 已将管理员关联到公司: {tenant.name}")
        else:
            print(f"  ✓ 管理员已关联到公司: {tenant.name}")
    except UserProfile.DoesNotExist:
        print("  创建 UserProfile...")
        profile = UserProfile.objects.create(user=admin_user, tenant=tenant)
        print(f"  ✓ 已创建 UserProfile 并关联到公司: {tenant.name}")
else:
    print("\n⚠ 未找到超级管理员")

print("\n✅ 数据库初始化完成！")
