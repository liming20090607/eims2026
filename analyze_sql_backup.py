#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析SQL备份文件中的数据量
"""
import re
from collections import Counter

sql_file = 'eims_mysql_backup_utf8.sql'

print("=" * 80)
print(f"分析SQL备份文件: {sql_file}")
print("=" * 80)

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有INSERT INTO语句
    tables = re.findall(r'INSERT INTO `([^`]+)`', content)
    table_counts = Counter(tables)
    
    print(f"\n总INSERT语句数: {len(tables)}")
    print(f"涉及的表数量: {len(table_counts)}")
    
    print("\n各表记录数（前30个）:")
    print("-" * 80)
    for table, count in table_counts.most_common(30):
        print(f"  {table:50s} : {count:6d} 条")
    
    # 特别关注的表
    print("\n" + "=" * 80)
    print("重点关注的表:")
    print("=" * 80)
    key_tables = [
        'eims_app_contract',
        'eims_app_projectdetail',
        'eims_app_personnel', 
        'eims_app_employee',
        'auth_user',
        'eims_app_userprofile'
    ]
    
    for table in key_tables:
        count = table_counts.get(table, 0)
        print(f"  {table:40s} : {count:6d} 条")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
