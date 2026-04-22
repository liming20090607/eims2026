"""
Initialize company databases with business tables only
UserProfile, UserTenantRelation, Tenant, TenantModule are ONLY in root_admin
Business tables (Employee, Project, Contract, etc.) are in each company database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.conf import settings
from django.db import connection, connections

DATABASES_TO_INIT = ['dingce', 'shengchang', 'jiachengda']

# Models that should ONLY be in root_admin (not in company databases)
ROOT_ADMIN_ONLY_MODELS = [
    'userprofile',
    'usertenantrelation', 
    'tenant',
    'tenantmodule',
    'tenantmodulepermission',
]

def init_company_database(db_name):
    """Initialize a company database with business tables only."""
    print(f"\n{'='*70}")
    print(f"初始化公司数据库: {db_name}")
    print(f"{'='*70}")
    
    # Step 1: Unfake all migrations
    print(f"\n步骤1: 重置 {db_name} 的迁移状态...")
    from django.core.management import call_command
    call_command('migrate', '--database', db_name, 'eims_app', 'zero', '--fake')
    print(f"✓ {db_name} 的迁移状态已重置")
    
    # Step 2: Fake Django core migrations (auth, admin, etc. are not in company DBs)
    print(f"\n步骤2: Fake Django核心应用的迁移 (auth, admin, sessions)...")
    call_command('migrate', '--database', db_name, 'auth', '--fake')
    call_command('migrate', '--database', db_name, 'admin', '--fake')
    call_command('migrate', '--database', db_name, 'contenttypes', '--fake')
    call_command('migrate', '--database', db_name, 'sessions', '--fake')
    print(f"✓ Django核心应用迁移已Fake")
    
    # Step 3: Fake UserProfile, Tenant and TenantModule related migrations (only in root_admin)
    print(f"\n步骤3: Fake用户认证相关迁移 (UserProfile, Tenant, TenantModule等)...")
    # Migration 0040: creates Tenant, Contract models
    # Migration 0041: adds UserTenantRelation
    # Migration 0042: creates TenantModule, TenantModulePermission (references Tenant)
    call_command('migrate', '--database', db_name, 'eims_app', '0042', '--fake')
    print(f"✓ 用户认证相关迁移已Fake")
    
    # Step 4: Run business table migrations
    print(f"\n步骤4: 应用业务表迁移...")
    call_command('migrate', '--database', db_name, 'eims_app')
    print(f"✓ 业务表迁移完成")
    
    # Step 5: Verify tables
    print(f"\n步骤5: 验证表是否创建成功...")
    cursor = connections[db_name].cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    eims_tables = [t for t in tables if t.startswith('eims_app_')]
    print(f"✓ {db_name} 数据库中共有 {len(eims_tables)} 个 eims_app 表:")
    for table in sorted(eims_tables):
        print(f"    - {table}")
    
    # Check that root_admin only models are NOT in company database
    for model in ROOT_ADMIN_ONLY_MODELS:
        table_name = f"eims_app_{model}"
        if table_name in eims_tables:
            print(f"⚠️  警告: {table_name} 不应在 {db_name} 中!")
        else:
            print(f"✓ {table_name} 正确地不在 {db_name} 中")
    
    print(f"\n✅ {db_name} 数据库初始化完成!")

def main():
    print("="*70)
    print("公司数据库初始化脚本")
    print("="*70)
    print("\n此脚本将为公司数据库创建业务表:")
    print("- Employee, Project, Contract, Notice, File, etc.")
    print("\n用户认证相关表 (UserProfile, Tenant, etc.) 仅在 root_admin 中:")
    print("- UserProfile, UserTenantRelation, Tenant, TenantModule")
    
    for db_name in DATABASES_TO_INIT:
        try:
            init_company_database(db_name)
        except Exception as e:
            print(f"\n❌ 初始化 {db_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n" + "="*70)
    print("✅ 所有公司数据库初始化完成!")
    print("="*70)
    return 0

if __name__ == '__main__':
    sys.exit(main())
