"""
检查 TenantModule 表是否存在及数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("检查 TenantModule 表")
print("=" * 80)

# 检查表是否存在
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES LIKE '%tenant%'")
    tables = cursor.fetchall()
    
    print(f"\n包含 'tenant' 的表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 检查具体的表
    target_tables = [
        'eims_app_tenantmodule',
        'eims_app_tenantmodulepermission',
        'eims_app_tenant',
    ]
    
    print(f"\n检查关键表:")
    for table_name in target_tables:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        exists = cursor.fetchone()
        if exists:
            print(f"  ✓ {table_name} 存在")
            
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    记录数: {count}")
        else:
            print(f"  ✗ {table_name} 不存在")

print("\n" + "=" * 80)
