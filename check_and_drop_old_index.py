"""
检查并删除旧的 employee_code 唯一索引
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("检查 eims_app_employee 表的索引")
print("=" * 80)

cursor = connection.cursor()

# 查看所有索引
cursor.execute("SHOW INDEX FROM eims_app_employee")
indexes = cursor.fetchall()

print("\n📋 所有索引:")
for idx in indexes:
    print(f"   - {idx[2]} (列: {idx[4]})")

# 查找包含 employee_code 的索引
print("\n🔍 查找包含 'employee_code' 的索引:")
old_indexes = [idx for idx in indexes if 'employee_code' in str(idx)]

if old_indexes:
    print(f"\n⚠️  找到 {len(old_indexes)} 个旧索引:")
    for idx in old_indexes:
        index_name = idx[2]
        print(f"   - {index_name}")
        
        # 询问是否删除
        confirm = input(f"\n是否删除索引 {index_name}? (yes/no): ").strip().lower()
        if confirm == 'yes':
            try:
                cursor.execute(f"DROP INDEX {index_name} ON eims_app_employee")
                print(f"✅ 已删除索引: {index_name}")
            except Exception as e:
                print(f"❌ 删除失败: {e}")
else:
    print("   ✅ 没有找到旧的 employee_code 索引")

print("\n" + "=" * 80)
