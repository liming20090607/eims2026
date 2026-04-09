import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Tables that need tenant_id (based on actual table names from check)
tables_needing_tenant = [
    'eims_app_Contract',  # 注意大写C
    'eims_app_approvalchain',
    'eims_app_approvalchain_cross_departments',
    'eims_app_approvalflow',
    'eims_app_approvalflowconfig',
    'eims_app_approvalrecord',
    'eims_app_archiveapprovalrecord',
    'eims_app_archiveattachment',
    'eims_app_contractapprovalrecord',
    'eims_app_contractattachment',
    'eims_app_departmentmanager',
    'eims_app_departmentrole',
    'eims_app_dynamicchoice',
    'eims_app_fileaccesspermission',
    'eims_app_filemanageversion',
    'eims_app_monthlyreport',
    'eims_app_noticeattachment',
    'eims_app_project',
    'eims_app_projectreporter',
    'eims_app_projectrole',
    'eims_app_qrcodeloginsession',
    'eims_app_role',
    'eims_app_sealapprovalrecord',
    'eims_app_sealattachment',
    'eims_app_smsverificationrecord',
    'eims_app_tenant',
    'eims_app_wechatqrcodesession',
    'eims_app_wechatuserbinding',
]

print("=== 补充添加 tenant_id 字段 ===\n")
added_count = 0
skipped_count = 0

for table in tables_needing_tenant:
    try:
        cursor.execute(f"""
            ALTER TABLE {table} 
            ADD COLUMN tenant_id INT NULL
        """)
        connection.commit()
        print(f"✓ {table}")
        added_count += 1
    except Exception as e:
        if "Duplicate column name" in str(e) or "1060" in str(e):
            print(f"  {table}: 已存在，跳过")
            skipped_count += 1
        else:
            print(f"✗ {table}: {e}")

print(f"\n✅ 完成！新增: {added_count} 个表, 跳过: {skipped_count} 个表")
