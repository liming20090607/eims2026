"""
清理旧部门数据（无租户前缀的部门编号）
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_department import Department
from eims_app.models.model_tenant import Tenant

def clean_old_departments():
    """删除所有没有租户前缀的部门编号"""
    print("="*70)
    print("清理旧部门数据")
    print("="*70)
    
    # 查找所有不符合新格式的部门编号（不包含 "-" 的）
    old_departments = Department.objects.using('root_admin').all()
    
    deleted_count = 0
    for dept in old_departments:
        # 如果部门编号不包含 "-"，说明是旧格式
        if '-' not in dept.department_code:
            print(f"删除旧部门: {dept.department_name} ({dept.department_code}) - 租户: {dept.tenant.short_name if dept.tenant else 'N/A'}")
            dept.delete()
            deleted_count += 1
    
    print(f"\n共删除 {deleted_count} 个旧部门")
    print("="*70)

if __name__ == '__main__':
    clean_old_departments()
