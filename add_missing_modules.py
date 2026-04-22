"""
添加缺失的业务模块到数据库
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant_module import TenantModule

def add_missing_modules():
    """添加工程监理、造价咨询等业务模块"""
    
    missing_modules = [
        {'code': 'supervision', 'name': '工程监理', 'description': '工程监理业务管理', 'icon': 'bi-clipboard2-check', 'sort_order': 7},
        {'code': 'cost', 'name': '造价咨询', 'description': '造价咨询业务管理', 'icon': 'bi-calculator', 'sort_order': 8},
        {'code': 'preparation', 'name': '前期准备', 'description': '项目前期准备工作', 'icon': 'bi-clipboard-data', 'sort_order': 9},
        {'code': 'bidding', 'name': '招标投标', 'description': '招标投标管理', 'icon': 'bi-trophy', 'sort_order': 10},
        {'code': 'design', 'name': '工程设计', 'description': '工程设计管理', 'icon': 'bi-pencil-square', 'sort_order': 11},
        {'code': 'construction', 'name': '工程施工', 'description': '工程施工管理', 'icon': 'bi-hammer', 'sort_order': 12},
        {'code': 'completion', 'name': '竣工验收', 'description': '竣工验收管理', 'icon': 'bi-check-circle', 'sort_order': 13},
    ]
    
    print("="*70)
    print("添加缺失的业务模块")
    print("="*70)
    
    added_count = 0
    for module_data in missing_modules:
        module, created = TenantModule.objects.get_or_create(
            code=module_data['code'],
            defaults={
                'name': module_data['name'],
                'description': module_data['description'],
                'icon': module_data['icon'],
                'sort_order': module_data['sort_order'],
                'is_active': True
            }
        )
        
        if created:
            print(f"✓ 添加模块: {module.name} ({module.code})")
            added_count += 1
        else:
            print(f"⊘ 模块已存在: {module.name} ({module.code})")
    
    print(f"\n共添加 {added_count} 个新模块")
    print("="*70)
    
    # 为所有租户启用新添加的模块
    print("\n为所有租户启用新模块...")
    from eims_app.models.model_tenant import Tenant
    from eims_app.models.model_tenant_module import TenantModulePermission
    
    tenants = Tenant.objects.all()
    new_modules = TenantModule.objects.filter(code__in=[m['code'] for m in missing_modules])
    
    enabled_count = 0
    for tenant in tenants:
        for module in new_modules:
            perm, created = TenantModulePermission.objects.using('root_admin').get_or_create(
                tenant=tenant,
                module=module,
                defaults={'is_enabled': True}
            )
            if created:
                print(f"  ✓ {tenant.short_name} - {module.name}: 已启用")
                enabled_count += 1
    
    print(f"\n共启用 {enabled_count} 个模块权限")
    print("="*70)

if __name__ == '__main__':
    add_missing_modules()
