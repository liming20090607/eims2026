"""
为 CompanyExecutiveRole 添加 tenant 字段并迁移现有数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection, transaction
from eims_app.models import Tenant, CompanyExecutiveRole

def migrate_executive_roles_to_tenants():
    """
    为现有的 CompanyExecutiveRole 记录分配租户
    策略：根据用户所属的租户来分配
    """
    
    print("=" * 80)
    print("开始迁移 CompanyExecutiveRole 数据到各租户...")
    print("=" * 80)
    
    with transaction.atomic():
        # 获取所有高管角色
        executives = CompanyExecutiveRole.objects.all()
        print(f"\n找到 {executives.count()} 条高管角色记录")
        
        if not executives.exists():
            print("没有需要迁移的数据")
            return
        
        migrated_count = 0
        skipped_count = 0
        
        for executive in executives:
            try:
                # 获取用户关联的租户
                from eims_app.models import UserTenantRelation
                
                # 查找用户的第一个租户
                user_tenant_relation = UserTenantRelation.objects.filter(
                    user=executive.user
                ).first()
                
                if user_tenant_relation:
                    # 分配租户
                    executive.tenant = user_tenant_relation.tenant
                    executive.save(update_fields=['tenant'])
                    migrated_count += 1
                    print(f"✓ {executive.user.username} - {executive.role_name} -> {executive.tenant.tenant_name}")
                else:
                    # 如果用户没有租户关联，跳过或分配到默认租户
                    print(f"⚠ {executive.user.username} - {executive.role_name} 没有关联的租户，跳过")
                    skipped_count += 1
                    
            except Exception as e:
                print(f"✗ 处理 {executive.user.username} 时出错: {e}")
                skipped_count += 1
        
        print("\n" + "=" * 80)
        print(f"迁移完成！")
        print(f"  成功迁移: {migrated_count} 条")
        print(f"  跳过: {skipped_count} 条")
        print("=" * 80)

if __name__ == '__main__':
    migrate_executive_roles_to_tenants()
