"""
清理已删除员工的人员编号，避免唯一索引冲突
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee
from django.db import connection

print("=" * 80)
print("清理已删除员工的人员编号")
print("=" * 80)

# 查找所有已删除但有人员编号的员工
deleted_with_codes = Employee.objects.filter(is_deleted=True).exclude(personnel_code__startswith='TEMP-').exclude(personnel_code='')

print(f"\n找到 {deleted_with_codes.count()} 名已删除但有编号的员工:\n")

for emp in deleted_with_codes:
    old_code = emp.personnel_code
    temp_code = f"DELETED-{emp.id}"
    print(f"  {old_code} → {temp_code} | {emp.name}")
    
    # 更新为临时编号
    Employee.objects.filter(id=emp.id).update(personnel_code=temp_code)

print("\n✅ 清理完成！现在可以安全地重新编号了。")
print("=" * 80)
