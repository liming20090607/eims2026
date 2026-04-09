import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import (
    Tenant, ProjectDetail, Contract, Personnel, Employee,
    ContractApproval, ArchiveApproval, SealApproval,
    ProjectDynamic, OutputPayment, Notice, FileManage,
    PersonnelCertificate, PersonnelAllocation, Department
)

print("="*60)
print("为现有数据分配默认租户")
print("="*60)
print()

# 获取默认租户（甲公司）
try:
    default_tenant = Tenant.objects.get(code='COMPANY_A')
    print(f"✅ 找到默认租户: {default_tenant.name} ({default_tenant.code})")
except Tenant.DoesNotExist:
    print("❌ 错误: 找不到默认租户（甲公司）")
    print("请先运行: python manage.py migrate_tenants")
    exit(1)

print()

# 定义需要迁移的模型列表
models_to_migrate = [
    ('ProjectDetail', ProjectDetail),
    ('Contract', Contract),
    ('Personnel', Personnel),
    ('Employee', Employee),
    ('ContractApproval', ContractApproval),
    ('ArchiveApproval', ArchiveApproval),
    ('SealApproval', SealApproval),
    ('ProjectDynamic', ProjectDynamic),
    ('OutputPayment', OutputPayment),
    ('Notice', Notice),
    ('FileManage', FileManage),
    ('PersonnelCertificate', PersonnelCertificate),
    ('PersonnelAllocation', PersonnelAllocation),
    ('Department', Department),
]

total_updated = 0

for model_name, model_class in models_to_migrate:
    try:
        # 统计未分配租户的记录数
        unassigned_count = model_class.objects.filter(tenant__isnull=True).count()
        
        if unassigned_count > 0:
            # 更新这些记录
            updated_count = model_class.objects.filter(
                tenant__isnull=True
            ).update(tenant=default_tenant)
            
            total_updated += updated_count
            print(f"✅ {model_name}: {updated_count} 条记录已分配到 {default_tenant.name}")
        else:
            print(f"⏭️  {model_name}: 无需迁移（所有记录已有租户）")
    
    except Exception as e:
        print(f"❌ {model_name}: 迁移失败 - {str(e)}")

print()
print("="*60)
print(f"✅ 数据迁移完成！共更新 {total_updated} 条记录")
print(f"   所有数据现已归属于: {default_tenant.name}")
print("="*60)
