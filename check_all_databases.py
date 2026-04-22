"""
检查所有数据库中的员工数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

databases = ['default', 'dingce', 'shengchang', 'jiachengda']

print("=" * 80)
print("检查所有数据库中的鼎策公司员工")
print("=" * 80)

for db_name in databases:
    print(f"\n📊 数据库: {db_name}")
    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute("""
                SELECT id, personnel_code, name, tenant_id 
                FROM eims_app_employee 
                WHERE is_deleted = 0 
                AND personnel_code LIKE 'DCRY-%'
                ORDER BY personnel_code
            """)
            rows = cursor.fetchall()
            
            if rows:
                print(f"   找到 {len(rows)} 名 DCRY 员工:")
                for row in rows:
                    print(f"      - ID:{row[0]} | {row[1]} | {row[2]} | tenant_id:{row[3]}")
            else:
                print(f"   ✅ 没有找到 DCRY 员工")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

print("\n" + "=" * 80)
