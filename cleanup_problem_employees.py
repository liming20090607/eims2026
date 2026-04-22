"""
删除所有数据库中的问题数据：
1. 编号重复的员工（保留最早创建的）
2. 无公司的员工
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

databases = ['default', 'dingce', 'shengchang', 'jiachengda']

print("=" * 80)
print("清理所有数据库中的问题数据")
print("=" * 80)

total_deleted = 0

for db_name in databases:
    print(f"\n{'='*60}")
    print(f"📊 处理数据库: {db_name}")
    print(f"{'='*60}")
    
    try:
        with connections[db_name].cursor() as cursor:
            # 1. 删除无公司的员工
            cursor.execute("""
                SELECT id, personnel_code, name
                FROM eims_app_employee
                WHERE is_deleted = 0
                AND tenant_id IS NULL
                AND personnel_code NOT LIKE 'TEMP-%%'
                AND personnel_code NOT LIKE 'DELETED-%%'
            """)
            no_tenant_emps = cursor.fetchall()
            
            if no_tenant_emps:
                print(f"\n🗑️  删除 {len(no_tenant_emps)} 名无公司员工:")
                for emp in no_tenant_emps:
                    print(f"   - ID:{emp[0]} | {emp[1]} | {emp[2]}")
                    cursor.execute("DELETE FROM eims_app_employee WHERE id = %s", [emp[0]])
                    total_deleted += 1
                print(f"   ✅ 已删除")
            else:
                print("\n✅ 无公司员工")
            
            # 2. 检查并处理重复编号
            cursor.execute("""
                SELECT personnel_code, COUNT(*) as cnt, MIN(id) as min_id
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
                print(f"\n⚠️  发现 {len(duplicates)} 个重复编号，正在处理...")
                for dup in duplicates:
                    code = dup[0]
                    keep_id = dup[2]  # 保留ID最小的
                    
                    # 获取所有重复的记录
                    cursor.execute("""
                        SELECT id, name, create_time
                        FROM eims_app_employee
                        WHERE personnel_code = %s AND is_deleted = 0 AND id != %s
                    """, [code, keep_id])
                    
                    to_delete = cursor.fetchall()
                    print(f"\n   编号 {code}:")
                    print(f"      保留: ID={keep_id}")
                    
                    for emp in to_delete:
                        print(f"      删除: ID={emp[0]} | {emp[1]} | created={emp[2]}")
                        cursor.execute("DELETE FROM eims_app_employee WHERE id = %s", [emp[0]])
                        total_deleted += 1
            else:
                print("\n✅ 无重复编号")
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print(f"✅ 清理完成！共删除 {total_deleted} 条记录")
print("=" * 80)

