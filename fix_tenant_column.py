"""
检查并修复所有数据库中的 tenant 表 project_code_prefix 列
"""
import os
import sys
import django

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections
from django.conf import settings

databases = ['default', 'dingce', 'shengchang', 'jiachengda', 'root_admin']

print("=" * 70)
print("检查并修复所有数据库中的 tenant 表")
print("=" * 70)

for db_name in databases:
    actual_db = settings.DATABASES[db_name].get('NAME', db_name)
    print(f"\n[{db_name}] -> MySQL database: {actual_db}")
    
    try:
        with connections[db_name].cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'eims_app_tenant'
            """, [actual_db])
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print(f"  ⚠️  表 eims_app_tenant 不存在")
                continue
            
            print(f"  ✅ 表存在")
            
            # Check if column exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'eims_app_tenant' 
                AND COLUMN_NAME = 'project_code_prefix'
            """, [actual_db])
            column_exists = cursor.fetchone()[0]
            
            if column_exists:
                print(f"  ✅ project_code_prefix 列已存在")
            else:
                print(f"  ❌ project_code_prefix 列不存在，正在添加...")
                cursor.execute(f"""
                    ALTER TABLE {actual_db}.eims_app_tenant 
                    ADD COLUMN project_code_prefix VARCHAR(10) DEFAULT '' 
                    COMMENT '项目编号前缀'
                """)
                print(f"  ✅ 列添加成功！")
                
    except Exception as e:
        print(f"  ⚠️  错误: {str(e)}")

print("\n" + "=" * 70)
print("✅ 检查完成！")
