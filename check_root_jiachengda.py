#!/usr/bin/env python
"""
全面检查eims_root数据库中的嘉诚达人员数据
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import pymysql

print("=" * 70)
print("全面检查eims_root数据库中的嘉诚达人员数据")
print("=" * 70)

conn_root = pymysql.connect(
    host='localhost', port=3306, user='root', password='root123',
    database='eims_root', charset='utf8mb4'
)
cursor_root = conn_root.cursor()

# 检查所有嘉诚达相关人员（tenant_id=4）
print("\n--- 所有tenant_id=4的人员记录 ---")
cursor_root.execute("""
    SELECT personnel_code, name, department, position, tenant_id, is_deleted
    FROM eims_app_personnel 
    WHERE tenant_id = 4
    ORDER BY personnel_code
""")
all_jcd = cursor_root.fetchall()
print(f"总记录数: {len(all_jcd)}")
for row in all_jcd:
    deleted_mark = "[已删除]" if row[5] else ""
    print(f"  {row[0]}: {row[1] or 'NULL'} (部门: {row[2] or 'NULL'}) {deleted_mark}")

# 检查所有以JCDRY开头的人员（无论tenant_id）
print("\n--- 所有JCDRY开头的人员记录 ---")
cursor_root.execute("""
    SELECT personnel_code, name, department, position, tenant_id, is_deleted
    FROM eims_app_personnel 
    WHERE personnel_code LIKE 'JCDRY%'
    ORDER BY personnel_code
""")
all_jcdry = cursor_root.fetchall()
print(f"总记录数: {len(all_jcdry)}")
for row in all_jcdry:
    deleted_mark = "[已删除]" if row[5] else ""
    print(f"  {row[0]}: {row[1] or 'NULL'} (部门: {row[2] or 'NULL'}, tenant: {row[4]}) {deleted_mark}")

# 检查Employee表（员工基础信息）
print("\n--- eims_root中Employee表 ---")
cursor_root.execute("SHOW TABLES LIKE 'eims_app_employee'")
tables = cursor_root.fetchall()
if tables:
    cursor_root.execute("""
        SELECT employee_code, name, gender, is_deleted 
        FROM eims_app_employee 
        ORDER BY employee_code 
        LIMIT 20
    """)
    emps = cursor_root.fetchall()
    print(f"员工记录: {len(emps)}")
    for row in emps:
        deleted_mark = "[已删除]" if row[3] else ""
        print(f"  {row[0]}: {row[1] or 'NULL'} {deleted_mark}")
else:
    print("无Employee表")

cursor_root.close()
conn_root.close()

print("\n完成!")
