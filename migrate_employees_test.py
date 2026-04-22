#!/usr/bin/env python
"""
Script to migrate employees from Dingce tenant to Jiachengda tenant for testing
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, 'E:\\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee, Tenant

def main():
    print("=" * 80)
    print("Employee Migration Script")
    print("=" * 80)
    
    # Get tenants
    try:
        dingce = Tenant.objects.get(name='广西鼎策工程顾问有限责任公司')
        jiachengda = Tenant.objects.get(name='广西嘉诚达工程造价咨询有限公司')
        shengchang = Tenant.objects.get(name='广西晟昌工程科技有限责任公司')
        
        print(f"\nTenants found:")
        print(f"  Dingce ID: {dingce.id}")
        print(f"  Jiachengda ID: {jiachengda.id}")
        print(f"  Shengchang ID: {shengchang.id}")
        
    except Tenant.DoesNotExist as e:
        print(f"Error: Tenant not found - {e}")
        return
    
    # Check current distribution
    print(f"\nCurrent employee distribution:")
    print(f"  Dingce: {Employee.objects.filter(tenant_id=dingce.id).count()}")
    print(f"  Jiachengda: {Employee.objects.filter(tenant_id=jiachengda.id).count()}")
    print(f"  Shengchang: {Employee.objects.filter(tenant_id=shengchang.id).count()}")
    print(f"  No tenant: {Employee.objects.filter(tenant__isnull=True).count()}")
    
    # Migrate some employees to Jiachengda (first 10 active employees from Dingce)
    employees_to_migrate = Employee.objects.filter(tenant_id=dingce.id, is_deleted=False)[:10]
    
    if employees_to_migrate.count() == 0:
        print("\nNo employees found to migrate!")
        return
    
    print(f"\nMigrating {employees_to_migrate.count()} employees from Dingce to Jiachengda...")
    
    count = 0
    for emp in employees_to_migrate:
        old_tenant_id = emp.tenant_id
        emp.tenant_id = jiachengda.id
        emp.save()
        count += 1
        print(f"  [{count}] {emp.employee_code} - {emp.name}: Tenant {old_tenant_id} -> {jiachengda.id}")
    
    print(f"\n✓ Successfully migrated {count} employees!")
    
    # Verify new distribution
    print(f"\nNew employee distribution:")
    print(f"  Dingce: {Employee.objects.filter(tenant_id=dingce.id).count()}")
    print(f"  Jiachengda: {Employee.objects.filter(tenant_id=jiachengda.id).count()}")
    print(f"  Shengchang: {Employee.objects.filter(tenant_id=shengchang.id).count()}")
    print(f"  No tenant: {Employee.objects.filter(tenant__isnull=True).count()}")
    
    print("\n" + "=" * 80)
    print("Migration completed successfully!")
    print("=" * 80)

if __name__ == '__main__':
    main()
