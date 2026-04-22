"""
自动删除旧的 employee_code 索引
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("自动删除旧的 employee_code 索引")
print("=" * 80)

cursor = connection.cursor()

# 查找包含 employee_code 的索引
cursor.execute("SHOW INDEX FROM eims_app_employee")
indexes = cursor.fetchall()

old_indexes = [idx for idx in indexes if idx[2] == 'employee_code']

if old_indexes:
    for idx in old_indexes:
        index_name = idx[2]
        print(f"\n🗑️  正在删除旧索引: {index_name}")
        try:
            cursor.execute(f"DROP INDEX {index_name} ON eims_app_employee")
            print(f"✅ 成功删除索引: {index_name}")
        except Exception as e:
            print(f"❌ 删除失败: {e}")
else:
    print("\n✅ 没有找到需要删除的旧索引")

print("\n" + "=" * 80)
print("完成！")
print("=" * 80)
