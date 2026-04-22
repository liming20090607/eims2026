#!/usr/bin/env python
import pymysql

# 连接 MySQL（无密码）
conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8mb4')
cursor = conn.cursor()

# 显示所有数据库
cursor.execute('SHOW DATABASES')
all_dbs = [db[0] for db in cursor.fetchall()]
print('所有数据库:')
for db in all_dbs:
    print(f'  - {db}')

# 创建开发数据库
cursor.execute('CREATE DATABASE IF NOT EXISTS eims2026_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
print('\n✅ 已创建/确认数据库: eims2026_dev')

conn.close()
