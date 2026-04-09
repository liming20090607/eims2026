import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("=== 检查 eims_app_tenant 表结构 ===\n")
cursor.execute("DESCRIBE eims_app_tenant")
columns = cursor.fetchall()

expected_fields = [
    'id', 'code', 'name', 'short_name', 'logo',
    'contact_person', 'contact_phone', 'contact_email',
    'address', 'is_active', 'remark', 'create_time', 'update_time'
]

print("实际字段:")
actual_fields = []
for col in columns:
    field_name = col[0]
    actual_fields.append(field_name)
    marker = " ✓" if field_name in expected_fields else " (意外字段)"
    print(f"  - {field_name} ({col[1]}){marker}")

print("\n缺少的字段:")
for field in expected_fields:
    if field not in actual_fields:
        print(f"  ✗ {field}")

if all(f in actual_fields for f in expected_fields):
    print("  (无，所有字段都存在)")

# 测试直接查询
print("\n测试查询:")
try:
    from eims_app.models.model_tenant import Tenant
    tenants = Tenant.objects.filter(is_active=True)
    print(f"  查询成功，数量: {tenants.count()}")
    for t in tenants:
        print(f"  - {t.name} (code={t.code}, short_name={getattr(t, 'short_name', 'N/A')})")
except Exception as e:
    print(f"  查询失败: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ 检查完成！")
