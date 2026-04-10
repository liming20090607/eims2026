"""
初始化业务模块和租户权限数据
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_tenant_module import TenantModule, TenantModulePermission


def init_tenant_modules():
    """初始化7个业务模块"""
    modules_data = [
        {'code': 'preparation', 'name': '前期准备', 'icon': 'bi-clipboard-data', 'sort_order': 1},
        {'code': 'bidding', 'name': '招标投标', 'icon': 'bi-trophy', 'sort_order': 2},
        {'code': 'design', 'name': '工程设计', 'icon': 'bi-pencil-square', 'sort_order': 3},
        {'code': 'cost', 'name': '造价咨询', 'icon': 'bi-calculator', 'sort_order': 4},
        {'code': 'supervision', 'name': '工程监理', 'icon': 'bi-clipboard2-check', 'sort_order': 5},
        {'code': 'construction', 'name': '工程施工', 'icon': 'bi-hammer', 'sort_order': 6},
        {'code': 'testing', 'name': '工程检测', 'icon': 'bi-search', 'sort_order': 7},
    ]
    
    print("=" * 60)
    print("初始化业务模块...")
    print("=" * 60)
    
    for module_data in modules_data:
        module, created = TenantModule.objects.get_or_create(
            code=module_data['code'],
            defaults={
                'name': module_data['name'],
                'icon': module_data['icon'],
                'sort_order': module_data['sort_order'],
                'is_active': True,
            }
        )
        if created:
            print(f"  ✓ 创建模块: {module.name} ({module.code})")
        else:
            print(f"  - 模块已存在: {module.name}")
    
    print(f"\n✅ 业务模块初始化完成，共 {TenantModule.objects.count()} 个模块\n")


def init_tenant_module_permissions():
    """为所有租户创建默认模块权限（全部启用）"""
    tenants = Tenant.objects.filter(is_active=True)
    modules = TenantModule.objects.filter(is_active=True)
    
    print("=" * 60)
    print("初始化租户模块权限...")
    print("=" * 60)
    
    total_created = 0
    
    for tenant in tenants:
        print(f"\n📋 为 {tenant.name} 创建权限:")
        for module in modules:
            perm, created = TenantModulePermission.objects.get_or_create(
                tenant=tenant,
                module=module,
                defaults={'is_enabled': True}
            )
            if created:
                total_created += 1
                print(f"  ✓ {module.name}: 启用")
            else:
                print(f"  - {module.name}: 已存在")
    
    print(f"\n✅ 权限初始化完成，共创建 {total_created} 条权限记录\n")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("租户模块权限初始化脚本")
    print("=" * 60 + "\n")
    
    init_tenant_modules()
    init_tenant_module_permissions()
    
    print("=" * 60)
    print("🎉 所有初始化完成！")
    print("=" * 60)
    print("\n下一步操作:")
    print("1. 访问 Django Admin: http://localhost:8000/admin/")
    print("2. 进入'租户公司管理'，编辑公司")
    print("3. 在'业务模块权限'部分勾选/取消勾选需要启用的模块")
    print("4. 保存后，侧边栏将根据权限自动显示/隐藏模块")
    print("\n")


if __name__ == '__main__':
    main()
