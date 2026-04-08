"""
EIMS SQLite Data Export Tool
Export data from SQLite avoiding broken references
"""
import os
import sys
import sqlite3
import json

project_root = os.path.dirname(os.path.abspath(__file__))
sqlite_path = os.path.join(project_root, 'db.sqlite3')
output_path = os.path.join(project_root, 'sqlite_backup.json')

print("=" * 60)
print("EIMS SQLite Data Export Tool")
print("=" * 60)

# Connect to SQLite
conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'django_%' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cursor.fetchall()]

print(f"\nFound {len(tables)} business tables in SQLite\n")

# Export data
data = []
total_records = 0

for table in tables:
    try:
        # Check if table is empty
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        if count == 0:
            continue
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Convert to Django fixture format using proper model mapping
        # Map SQLite table names to Django model names
        model_map = {
            'auth_user': 'auth.user',
            'auth_group': 'auth.group',
            'auth_permission': 'auth.permission',
            'auth_group_permissions': 'auth.group_permissions',
            'auth_user_groups': 'auth.user_groups',
            'auth_user_user_permissions': 'auth.user_user_permissions',
            'eims_app_userprofile': 'eims_app.userprofile',
            'eims_app_role': 'eims_app.role',
            'eims_app_department': 'eims_app.department',
            'eims_app_approvalchain': 'eims_app.approvalchain',
            'eims_app_approvalchain_cross_departments': 'eims_app.approvalchain_cross_departments',
            'eims_app_departmentrole': 'eims_app.departmentrole',
            'eims_app_departmentmanager': 'eims_app.departmentmanager',
            'eims_app_filemanage': 'eims_app.filemanage',
            'eims_app_filemanageversion': 'eims_app.filemanageversion',
            'eims_app_fileaccesspermission': 'eims_app.fileaccesspermission',
            'eims_app_employee': 'eims_app.employee',
            'eims_app_monthlyreport': 'eims_app.monthlyreport',
            'eims_app_project': 'eims_app.project',
            'eims_app_projectdetail': 'eims_app.projectdetail',
            'eims_app_projectdynamic': 'eims_app.projectdynamic',
            'eims_app_projectreporter': 'eims_app.projectreporter',
            'eims_app_projectrole': 'eims_app.projectrole',
            'eims_app_contract': 'eims_app.contract',
            'eims_app_contractapproval': 'eims_app.contractapproval',
            'eims_app_contractapprovalrecord': 'eims_app.contractapprovalrecord',
            'eims_app_contractattachment': 'eims_app.contractattachment',
            'eims_app_outputpayment': 'eims_app.outputpayment',
            'eims_app_personnel': 'eims_app.personnel',
            'eims_app_personnelcertificate': 'eims_app.personnelcertificate',
            'eims_app_personnelallocation': 'eims_app.personnelallocation',
            'eims_app_notice': 'eims_app.notice',
            'eims_app_noticeattachment': 'eims_app.noticeattachment',
            'eims_app_smsverificationrecord': 'eims_app.smsverificationrecord',
            'eims_app_qrcodeloginsession': 'eims_app.qrcodeloginsession',
            'eims_app_approvalflow': 'eims_app.approvalflow',
            'eims_app_approvalflowconfig': 'eims_app.approvalflowconfig',
            'eims_app_approvalrecord': 'eims_app.approvalrecord',
            'eims_app_archiveapproval': 'eims_app.archiveapproval',
            'eims_app_archiveattachment': 'eims_app.archiveattachment',
            'eims_app_archiveapprovalrecord': 'eims_app.archiveapprovalrecord',
            'eims_app_sealapproval': 'eims_app.sealapproval',
            'eims_app_sealattachment': 'eims_app.sealattachment',
            'eims_app_sealapprovalrecord': 'eims_app.sealapprovalrecord',
            'eims_app_dynamicchoice': 'eims_app.dynamicchoice',
            'eims_app_wechatuserbinding': 'eims_app.wechatuserbinding',
            'eims_app_wechatqrcodesession': 'eims_app.wechatqrcodesession',
            'eims_app_allocation_department': 'eims_app.allocation_department',
            'eims_app_allocation_personnel': 'eims_app.allocation_personnel',
        }
        
        model_path = model_map.get(table, f'eims_app.{table}')
        
        # Skip Django system tables
        if table.startswith('django_'):
            continue
        
        for row in rows:
            record = {
                'model': model_path,
                'pk': row[0],  # Assume first column is primary key
                'fields': {}
            }
            
            for i, col in enumerate(columns[1:], 1):  # Skip primary key
                record['fields'][col] = row[i]
            
            data.append(record)
            total_records += 1
        
        print(f"  ✓ {table}: {count} records")
        
    except Exception as e:
        print(f"  ✗ {table}: Error - {e}")

# Write to JSON
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

file_size = os.path.getsize(output_path)
print(f"\n{'=' * 60}")
print(f"Export Complete!")
print(f"Total records: {total_records}")
print(f"File: {output_path}")
print(f"Size: {file_size / 1024:.1f} KB")
print(f"{'=' * 60}")

conn.close()
