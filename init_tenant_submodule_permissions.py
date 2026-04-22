"""
为所有租户初始化子模块权限
确保每个租户都能看到所有已启用一级模块下的子模块
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_sub_module import SubModule, TenantSubModulePermission
from eims_app.models.model_tenant_module import TenantModulePermission

def init_tenant_submodule_permissions():
    """为所有租户创建子模块权限"""
    
    print("="*80)
    print("租户子模块权限初始化")
    print("="*80)
    
    # 获取所有启用的租户
    tenants = Tenant.objects.filter(is_active=True)
    
    if not tenants.exists():
        print("\n❌ 没有找到启用的租户")
        return
    
    total_created = 0
    total_skipped = 0
    
    for tenant in tenants:
        print(f"\n📋 处理租户: {tenant.name}")
        print("-" * 80)
        
        # 获取该租户已启用的一级模块
        enabled_modules = TenantModulePermission.objects.filter(
            tenant=tenant,
            is_enabled=True
        ).values_list('module', flat=True)
        
        if not enabled_modules:
            print(f"  ⚠ 该租户没有启用任何一级模块，跳过子模块权限设置")
            continue
        
        # 获取这些一级模块下的所有活跃子模块
        submodules = SubModule.objects.filter(
            parent_module__in=enabled_modules,
            is_active=True
        )
        
        if not submodules.exists():
            print(f"  ⚠ 没有找到可用的子模块")
            continue
        
        print(f"  找到 {submodules.count()} 个子模块")
        
        # 为每个子模块创建权限记录
        for submodule in submodules:
            perm, created = TenantSubModulePermission.objects.get_or_create(
                tenant=tenant,
                sub_module=submodule,
                defaults={'is_enabled': True}
            )
            
            if created:
                total_created += 1
                print(f"  ✓ 创建: {submodule.name}")
            else:
                total_skipped += 1
                if not perm.is_enabled:
                    # 如果之前被禁用了，重新启用
                    perm.is_enabled = True
                    perm.save()
                    print(f"  ↻ 重新启用: {submodule.name}")
                else:
                    print(f"  - 已存在: {submodule.name}")
    
    # 统计信息
    print("\n" + "="*80)
    print("初始化完成!")
    print("="*80)
    print(f"  ✓ 新建: {total_created} 条权限记录")
    print(f"  ↻ 更新: {TenantSubModulePermission.objects.filter(is_enabled=True).count() - (TenantSubModulePermission.objects.count() - total_created - total_skipped)} 条记录")
    print(f"  - 跳过: {total_skipped} 条记录")
    print(f"  总计: {TenantSubModulePermission.objects.count()} 条权限记录")
    print("="*80)


if __name__ == '__main__':
    try:
        init_tenant_submodule_permissions()
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
