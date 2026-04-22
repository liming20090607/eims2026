import pymysql
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.conf import settings
print('='*70)
print('Django 数据库配置')
print('='*70)
print(f"\nDATABASES 配置:")
for db_name, db_config in settings.DATABASES.items():
    print(f"\n{db_name}:")
    print(f"  ENGINE: {db_config.get('ENGINE')}")
    print(f"  NAME: {db_config.get('NAME')}")
    print(f"  USER: {db_config.get('USER')}")
    print(f"  HOST: {db_config.get('HOST')}")

print('\n' + '='*70)
print('检查 Personnel 表在各数据库中的状态')
print('='*70)

for db_name in ['root_admin', 'dingce', 'shengchang', 'jiachengda']:
    print(f"\n检查 {db_name} 数据库:")
    db_config = settings.DATABASES.get(db_name)
    if not db_config:
        print(f'  ✗ 数据库 {db_name} 未在配置中定义')
        continue
    
    try:
        import pymysql
        conn = pymysql.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config.get('USER', 'root'),
            password=db_config.get('PASSWORD', ''),
            database=db_config.get('NAME')
        )
        cursor = conn.cursor()
        
        # 检查 Personnel 表
        cursor.execute("SHOW TABLES LIKE 'eims_app_personnel'")
        tables = cursor.fetchall()
        
        if tables:
            print(f'  Personnel 表: 存在')
            cursor.execute("SELECT COUNT(*) FROM eims_app_personnel")
            count = cursor.fetchone()[0]
            print(f'  数据量: {count} 条')
            
            # 获取字段列表
            cursor.execute("DESCRIBE eims_app_personnel")
            columns = cursor.fetchall()
            field_names = [col[0] for col in columns]
            print(f'  字段: {len(field_names)} 个')
            if 'is_deleted' in field_names:
                print(f'  ✓ is_deleted: 存在')
            else:
                print(f'  ✗ is_deleted: 不存在')
            
            # 检查是否有外键到 ProjectDetail
            if 'project_id' in field_names:
                print(f'  ✓ project_id: 存在')
            if 'employee_id' in field_names:
                print(f'  ✓ employee_id: 存在')
        else:
            print(f'  ✗ Personnel 表: 不存在')
            
        # 检查 ProjectDetail 表
        cursor.execute("SHOW TABLES LIKE 'eims_app_projectdetail'")
        tables = cursor.fetchall()
        if tables:
            print(f'  ProjectDetail 表: 存在')
            cursor.execute("SELECT COUNT(*) FROM eims_app_projectdetail")
            count = cursor.fetchone()[0]
            print(f'  数据量: {count} 条')
        else:
            print(f'  ✗ ProjectDetail 表: 不存在')
        
        conn.close()
    except Exception as e:
        print(f'  错误: {e}')

print('\n' + '='*70)
