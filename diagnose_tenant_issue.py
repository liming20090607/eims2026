"""
诊断造价咨询项目信息的tenant字段问题
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import CostProjectUnified

print("=" * 60)
print("  造价咨询项目信息 - Tenant字段诊断")
print("=" * 60)

# 查询所有记录
all_records = CostProjectUnified.objects.all()
print(f"\n总记录数: {all_records.count()}")

print("\n所有记录的tenant情况:")
for record in all_records:
    print(f"  ID={record.id}, 编号={record.project_code}, 名称={record.project_name[:20]}, tenant={record.tenant}")

print("\n有tenant的记录:")
records_with_tenant = all_records.filter(tenant__isnull=False)
print(f"  数量: {records_with_tenant.count()}")

print("\n没有tenant的记录:")
records_without_tenant = all_records.filter(tenant__isnull=True)
print(f"  数量: {records_without_tenant.count()}")

if records_without_tenant.exists():
    print("\n⚠️  问题发现: 存在tenant为NULL的记录!")
    print("   这些记录在列表中将不可见（被租户过滤器过滤掉）")
else:
    print("\n✓ 所有记录都有tenant值")

print("\n" + "=" * 60)
