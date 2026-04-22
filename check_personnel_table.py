#!/usr/bin/env python
"""
检查所有数据库中Personnel表的结构
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

import pymysql

# 数据库配置
databases = {
    'default': 'eims_dingce',
    'dingce': 'eims_dingce',
    'shengchang': 'eims_shengchang',
    'jiachengda': 'eims_jiachengda',
    'root_admin': 'eims_root',
}

print("=" * 60)
print("检查所有数据库中 eims_app_personnel 表的结构")
print("=" * 60)

for db_alias, db_name in databases.items():
    print(f"\n数据库别名: {db_alias} (数据库名: {db_name})")
    print("-" * 60)
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root123',
            database=db_name
        )
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'eims_app_personnel'")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"  ✗ 表 eims_app_personnel 不存在")
            conn.close()
            continue
        
        print(f"  ✓ 表 eims_app_personnel 存在")
        
        # 获取表结构
        cursor.execute("DESCRIBE eims_app_personnel")
        fields = cursor.fetchall()
        
        print(f"  字段列表 (共 {len(fields)} 个):")
        has_is_deleted = False
        for field in fields:
            field_name = field[0]
            print(f"    - {field_name}")
            if field_name == 'is_deleted':
                has_is_deleted = True
        
        if has_is_deleted:
            print(f"  ✓ 包含 is_deleted 字段")
        else:
            print(f"  ✗ 缺少 is_deleted 字段!")
        
        # 查询记录数
        cursor.execute("SELECT COUNT(*) FROM eims_app_personnel")
        count = cursor.fetchone()[0]
        print(f"  记录数: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
