#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清空嘉诚达数据库并重新执行迁移
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import pymysql

print("=" * 80)
print("  清空嘉诚达数据库并重新迁移")
print("=" * 80)

try:
    # 连接到MySQL服务器
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root123',
        port=3306,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # 删除所有表
    print("\n[步骤 1] 删除嘉诚达数据库中的所有表")
    print("-" * 80)
    cursor.execute("DROP DATABASE IF EXISTS eims_jiachengda;")
    print("  ✓ 已删除数据库 eims_jiachengda")
    
    # 重新创建数据库
    print("\n[步骤 2] 重新创建数据库")
    print("-" * 80)
    cursor.execute("""
        CREATE DATABASE eims_jiachengda 
        DEFAULT CHARACTER SET utf8mb4 
        DEFAULT COLLATE utf8mb4_unicode_ci;
    """)
    print("  ✓ 数据库 eims_jiachengda 创建成功")
    
    cursor.close()
    connection.close()
    
    print("\n✅ 数据库清理完成！")
    print("\n现在可以执行迁移:")
    print("  python manage.py migrate --database=jiachengda")
    
except Exception as e:
    print(f"\n✗ 操作失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
