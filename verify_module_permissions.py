"""
验证租户模块权限配置
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_tenant_module import TenantModule, TenantModulePermission

print("="*80)
print("租户模块权限配置验证")
print("="*80)

tenants = Tenant.objects.all()

for tenant in tenants:
    print(f"\n{tenant.name} ({tenant.code}):")
    print("-" * 80)
    
    # 获取该租户的所有模块权限
    permissions = TenantModulePermission.objects.using('root_admin').filter(
        tenant=tenant
    ).select_related('module')
    
    enabled_modules = []
    disabled_modules = []
    
    for perm in permissions:
        if perm.is_enabled:
            enabled_modules.append(perm.module.name)
        else:
            disabled_modules.append(perm.module.name)
    
    print(f"  已启用模块 ({len(enabled_modules)}个):")
    for module_name in enabled_modules:
        print(f"    ✓ {module_name}")
    
    if disabled_modules:
        print(f"\n  未启用模块 ({len(disabled_modules)}个):")
        for module_name in disabled_modules:
            print(f"    ✗ {module_name}")

print("\n" + "="*80)
print("侧边栏显示说明:")
print("="*80)
print("""
侧边栏会根据 enabled_module_codes 列表显示对应的模块：

✅ 工程监理 (supervision) - 包含子菜单:
   - 合同管理
   - 项目管理  
   - 产值回款

✅ 造价咨询 (cost) - 待开发

✅ 前期准备 (preparation) - 待开发

✅ 招标投标 (bidding) - 待开发

✅ 工程设计 (design) - 待开发

✅ 工程施工 (construction) - 待开发

✅ 竣工验收 (completion) - 待开发

注意: 
- 只有当模块在 enabled_module_codes 中时才会显示
- 超级管理员可以看到所有模块
- 普通用户只能看到被授权的模块
""")

print("="*80)
print("验证完成!")
print("="*80)
