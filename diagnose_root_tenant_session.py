#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断 /root/ 路径下的 tenant 会话状态问题
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel, Tenant
import pymysql

print("=" * 80)
print("诊断：人员分配可视化页面的租户上下文问题")
print("=" * 80)

# 1. 检查所有租户信息
print("\n【1】租户信息:")
tenants = Tenant.objects.using('root_admin').all().order_by('id')
for t in tenants:
    print(f"  ID={t.id}, Code={t.code}, Name={t.name}")

# 2. 检查每个数据库中的 Personnel 记录数
print("\n【2】各数据库中 Personnel 记录统计:")
databases = {
    'dingce': 'eims_dingce',
    'shengchang': 'eims_shengchang', 
    'jiachengda': 'eims_jiachengda'
}

for db_alias, db_name in databases.items():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root123',
            database=db_name,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted = 0")
        count = cursor.fetchone()[0]
        
        # 按 tenant_id 分组统计
        cursor.execute("SELECT tenant_id, COUNT(*) FROM eims_app_personnel WHERE is_deleted = 0 GROUP BY tenant_id")
        tenant_counts = cursor.fetchall()
        
        print(f"\n  数据库: {db_name} ({db_alias})")
        print(f"    总记录数: {count}")
        for tid, cnt in tenant_counts:
            tenant_name = "未知"
            for t in tenants:
                if t.id == tid:
                    tenant_name = t.name
                    break
            print(f"      - tenant_id={tid} ({tenant_name}): {cnt} 条")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"\n  数据库: {db_name} ({db_alias}) - 连接失败: {e}")

# 3. 模拟视图逻辑（不带 tenant 过滤）
print("\n【3】模拟视图查询（无 tenant 过滤，使用默认路由）:")
try:
    # 这会触发数据库路由器，由于没有 request.tenant，会路由到 dingce 数据库
    all_personnel = Personnel.objects.filter(is_deleted=False)
    print(f"  查询结果: {all_personnel.count()} 条")
    
    # 按 department 分类
    unassigned = all_personnel.filter(
        department__isnull=True
    ).exclude(
        department__in=['', '未分配']
    )
    department_assigned = all_personnel.exclude(
        department__isnull=True
    ).exclude(
        department__in=[None, '', '未分配']
    )
    
    print(f"  待分配人员: {unassigned.count()} 条")
    print(f"  部门人员: {department_assigned.count()} 条")
except Exception as e:
    print(f"  查询失败: {e}")

# 4. 直接查询每个数据库验证数据存在性
print("\n【4】直接验证各数据库中的数据:")
for db_alias, db_name in databases.items():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root123',
            database=db_name,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 查询待分配人员（department 为空或 NULL 或 '未分配'）
        cursor.execute("""
            SELECT COUNT(*) FROM eims_app_personnel 
            WHERE is_deleted = 0 
            AND (department IS NULL OR department = '' OR department = '未分配')
            AND project_id IS NULL
            AND project2_id IS NULL
            AND project3_id IS NULL
            AND project4_id IS NULL
            AND project5_id IS NULL
        """)
        unassigned_count = cursor.fetchone()[0]
        
        # 查询部门人员（有 department 且不为空/NULL/'未分配'）
        cursor.execute("""
            SELECT COUNT(*) FROM eims_app_personnel 
            WHERE is_deleted = 0 
            AND department IS NOT NULL 
            AND department != '' 
            AND department != '未分配'
        """)
        dept_count = cursor.fetchone()[0]
        
        print(f"\n  {db_name}:")
        print(f"    待分配人员: {unassigned_count}")
        print(f"    部门人员: {dept_count}")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"\n  {db_name}: 查询失败 - {e}")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)
