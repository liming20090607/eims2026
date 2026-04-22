#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查嘉诚达数据库中 Personnel 记录的详细信息
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import pymysql

print("=" * 80)
print("检查嘉诚达数据库中的 Personnel 记录")
print("=" * 80)

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root123',
    database='eims_jiachengda',
    charset='utf8mb4'
)

cursor = connection.cursor(pymysql.cursors.DictCursor)

# 查询所有 Personnel 记录
cursor.execute("""
    SELECT id, personnel_code, name, department, 
           project_id, project2_id, project3_id, project4_id, project5_id,
           tenant_id, is_deleted
    FROM eims_app_personnel
    ORDER BY id
""")

records = cursor.fetchall()

print(f"\n总记录数: {len(records)}\n")

for record in records:
    print(f"ID={record['id']}, Code={record['personnel_code']}, Name={record['name']}")
    print(f"  Department: '{record['department']}' (type: {type(record['department']).__name__})")
    print(f"  Projects: p1={record['project_id']}, p2={record['project2_id']}, p3={record['project3_id']}, p4={record['project4_id']}, p5={record['project5_id']}")
    print(f"  Tenant ID: {record['tenant_id']}, Deleted: {record['is_deleted']}")
    
    # 判断分类
    all_projects_null = (
        record['project_id'] is None and
        record['project2_id'] is None and
        record['project3_id'] is None and
        record['project4_id'] is None and
        record['project5_id'] is None
    )
    
    dept_is_empty = (
        record['department'] is None or
        record['department'] == '' or
        record['department'] == '未分配'
    )
    
    if all_projects_null and dept_is_empty:
        category = "待分配人员"
    elif record['department'] is not None and record['department'] != '' and record['department'] != '未分配':
        category = "部门人员"
    else:
        category = "其他"
    
    print(f"  => 分类: {category}")
    print()

cursor.close()
connection.close()

print("=" * 80)
print("检查完成")
print("=" * 80)

