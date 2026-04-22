"""
为所有租户补全子模块权限
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_sub_module import SubModule, TenantSubModulePermission
from eims_app.models.model_tenant_module import TenantModulePermission

def fix_tenant_submodule_permissions():
    """补全租户子模块权限"""
    
    print("="*80)
    print("补全租户子模块权限")
    print("="*80)
    
    tenants = Tenant.objects.filter(is_active=True)
    total_created = 0
    total_updated = 0
    
    for tenant in tenants:
        print(f"\n📋 处理租户: {tenant.name}")
        print("-" * 80)
        
        # 获取该租户已启用的一级模块ID列表
        enabled_module_ids = list(
            TenantModulePermission.objects.filter(
                tenant=tenant,
                is_enabled=True
            ).values_list('module', flat=True)
        )
        
        if not enabled_module_ids:
            print(f"  ⚠ 该租户没有启用任何一级模块，跳过")
            continue
        
        # 获取这些一级模块下的所有活跃子模块
        submodules = SubModule.objects.filter(
            parent_module__in=enabled_module_ids,
            is_active=True
        )
        
        if not submodules.exists():
            print(f"  ⚠ 没有找到可用的子模块")
            continue
        
        print(f"  应分配 {submodules.count()} 个子模块权限")
        
        # 为每个子模块创建或更新权限记录
        for submodule in submodules:
            perm, created = TenantSubModulePermission.objects.get_or_create(
                tenant=tenant,
                sub_module=submodule,
                defaults={'is_enabled': True}
            )
            
            if created:
                total_created += 1
                print(f"  ✓ 创建: {submodule.parent_module.name} - {submodule.name}")
            elif not perm.is_enabled:
                # 如果之前被禁用了，重新启用
                perm.is_enabled = True
                perm.save()
                total_updated += 1
                print(f"  ↻ 重新启用: {submodule.parent_module.name} - {submodule.name}")
            else:
                print(f"  - 已存在: {submodule.parent_module.name} - {submodule.name}")
    
    # 统计信息
    print("\n" + "="*80)
    print("补全完成!")
    print("="*80)
    print(f"  ✓ 新建: {total_created} 条权限记录")
    print(f"  ↻ 重新启用: {total_updated} 条权限记录")
    print(f"  总计: {TenantSubModulePermission.objects.count()} 条权限记录")
    print("="*80)
    
    # 验证结果
    print("\n📋 验证结果:")
    print("-" * 80)
    for tenant in tenants:
        count = TenantSubModulePermission.objects.filter(tenant=tenant).count()
        print(f"  {tenant.name}: {count} 条子模块权限")


if __name__ == '__main__':
    try:
        fix_tenant_submodule_permissions()
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
