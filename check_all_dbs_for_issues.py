"""
检查所有数据库中的问题数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections
from django.db.models import Count

databases = ['default', 'dingce', 'shengchang', 'jiachengda']

print("=" * 80)
print("检查所有数据库中的问题数据")
print("=" * 80)

for db_name in databases:
    print(f"\n{'='*60}")
    print(f"📊 数据库: {db_name}")
    print(f"{'='*60}")
    
    try:
        with connections[db_name].cursor() as cursor:
            # 检查重复编号
            cursor.execute("""
                SELECT personnel_code, COUNT(*) as cnt
                FROM eims_app_employee
                WHERE is_deleted = 0
                AND personnel_code NOT LIKE 'TEMP-%%'
                AND personnel_code NOT LIKE 'DELETED-%%'
                AND personnel_code != ''
                GROUP BY personnel_code
                HAVING cnt > 1
            """)
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"\n⚠️  找到 {len(duplicates)} 个重复编号:")
                for dup in duplicates:
                    print(f"   - {dup[0]} (出现{dup[1]}次)")
            else:
                print("\n✅ 无重复编号")
            
            # 检查无公司员工
            cursor.execute("""
                SELECT id, personnel_code, name
                FROM eims_app_employee
                WHERE is_deleted = 0
                AND tenant_id IS NULL
                AND personnel_code NOT LIKE 'TEMP-%%'
                AND personnel_code NOT LIKE 'DELETED-%%'
            """)
            no_tenant = cursor.fetchall()
            
            if no_tenant:
                print(f"\n⚠️  找到 {len(no_tenant)} 名无公司员工:")
                for emp in no_tenant:
                    print(f"   - ID:{emp[0]} | {emp[1]} | {emp[2]}")
            else:
                print("\n✅ 无公司员工")
            
            # 统计
            cursor.execute("SELECT COUNT(*) FROM eims_app_employee WHERE is_deleted = 0")
            active_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM eims_app_employee WHERE is_deleted = 1")
            deleted_count = cursor.fetchone()[0]
            
            print(f"\n📈 统计: 活跃={active_count}, 已删除={deleted_count}")
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")

print("\n" + "=" * 80)
print("检查完成！")
print("=" * 80)
