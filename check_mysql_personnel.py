#!/usr/bin/env python
"""
检查数据库路由器和人员数据
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from eims_app.models import Personnel, Tenant
from django.db import connections

print("=" * 70)
print("检查人员数据在各MySQL数据库中的分布")
print("=" * 70)

# 直接查询MySQL数据库，不通过Django ORM
import pymysql

databases = {
    'eims_dingce': {'name': '鼎策', 'alias': 'dingce'},
    'eims_shengchang': {'name': '晟昌', 'alias': 'shengchang'},
    'eims_jiachengda': {'name': '嘉诚达', 'alias': 'jiachengda'},
}

for db_name, db_info in databases.items():
    print(f"\n--- MySQL数据库: {db_name} ({db_info['name']}) ---")
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root123',
            database=db_name,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 查询人员数量
        cursor.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted=0")
        count = cursor.fetchone()[0]
        print(f"  总人数: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT personnel_code, name, department, tenant_id 
                FROM eims_app_personnel 
                WHERE is_deleted=0 
                ORDER BY personnel_code 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            for row in rows:
                print(f"  - {row[0]}: {row[1] or 'NULL'} (部门: {row[2] or 'NULL'}, tenant_id: {row[3]})")
            if count > 10:
                print(f"  ... 还有 {count - 10} 人")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"  错误: {e}")

# 检查eims_root数据库中是否有人员数据
print(f"\n--- MySQL数据库: eims_root (root_admin) ---")
try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root123',
        database='eims_root',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    cursor.execute("SHOW TABLES LIKE 'eims_app_personnel'")
    tables = cursor.fetchall()
    if tables:
        cursor.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted=0")
        count = cursor.fetchone()[0]
        print(f"  总人数: {count}")
        if count > 0:
            cursor.execute("SELECT personnel_code, name, department FROM eims_app_personnel WHERE is_deleted=0 LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"  - {row[0]}: {row[1] or 'NULL'} (部门: {row[2] or 'NULL'})")
    else:
        print("  无人员表")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"  错误: {e}")
