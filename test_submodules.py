import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant_module import TenantModule, TenantModulePermission
from eims_app.models.model_sub_module import SubModule, TenantSubModulePermission
from eims_app.models import Tenant

print("=" * 60)
print("验证子模块权限配置")
print("=" * 60)

# 检查子模块
subs = SubModule.objects.filter(parent_module__code='approval').order_by('sort_order')
print(f"\n审批流程下的子模块 ({subs.count()} 个):")
for sub in subs:
    print(f"  - {sub.code}: {sub.name} (启用:{sub.is_active})")

# 检查租户权限
tenants = Tenant.objects.filter(is_active=True)
print(f"\n租户子模块权限:")
for tenant in tenants:
    perms = TenantSubModulePermission.objects.filter(tenant=tenant).select_related('sub_module')
    enabled = [p.sub_module.code for p in perms if p.is_enabled]
    disabled = [p.sub_module.code for p in perms if not p.is_enabled]
    
    print(f"\n{tenant.name}:")
    print(f"  ✓ 已启用: {enabled if enabled else '无'}")
    print(f"  ✗ 已禁用: {disabled if disabled else '无'}")

print("\n" + "=" * 60)
print("测试建议")
print("=" * 60)
print("1. 登录系统，查看侧边栏'审批流程'下的子菜单")
print("2. 所有子模块都应该可见（因为当前全部启用）")
print("3. 进入 Django Admin -> 租户公司管理")
print("4. 选择一个公司，在'子模块权限'中取消勾选某个子模块")
print("5. 保存后刷新系统页面，被禁用的子模块应该从侧边栏消失")
print("=" * 60)
