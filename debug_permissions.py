import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_sub_module import SubModule, TenantSubModulePermission
from eims_app.models.model_tenant_module import TenantModulePermission, TenantModule

# 检查租户的模块权限
tenants = Tenant.objects.filter(is_active=True)
for tenant in tenants:
    print(f"\n{'='*80}")
    print(f"租户: {tenant.name}")
    print(f"{'='*80}")
    
    # 获取该租户已启用的一级模块
    perms = TenantModulePermission.objects.filter(tenant=tenant, is_enabled=True)
    print(f"\n一级模块权限 (共{perms.count()}条):")
    for perm in perms:
        print(f"  - {perm.module.name} ({perm.module.code}) - 启用:{perm.is_enabled}")
    
    # 获取模块ID列表
    enabled_module_ids = list(perms.values_list('module', flat=True))
    print(f"\n已启用模块IDs: {enabled_module_ids}")
    
    # 查询这些模块下的子模块
    submodules = SubModule.objects.filter(parent_module__in=enabled_module_ids, is_active=True)
    print(f"可用子模块 (共{submodules.count()}个):")
    for sub in submodules:
        print(f"  - {sub.parent_module.name} - {sub.name} ({sub.code})")
    
    # 检查子模块权限
    sub_perms = TenantSubModulePermission.objects.filter(tenant=tenant)
    print(f"\n子模块权限 (共{sub_perms.count()}条):")
    for sub_perm in sub_perms:
        status = "✓" if sub_perm.is_enabled else "✗"
        print(f"  {status} {sub_perm.sub_module.name}")
