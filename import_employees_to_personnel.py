"""
从 Employee 表导入数据到 Personnel 表
快速补充人员花名册数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee, Personnel
from django.utils import timezone

print('=' * 80)
print('从 Employee 导入数据到 Personnel')
print('=' * 80)

# 获取所有未离职员工
employees = Employee.objects.filter(
    is_deleted=False,
    leave_time__isnull=True  # 未离职
)

print(f'\n找到 {employees.count()} 名在职员工')

created_count = 0
skipped_count = 0
error_count = 0

for emp in employees:
    try:
        # 检查是否已存在于 Personnel 表
        exists = Personnel.objects.filter(
            employee=emp,
            is_deleted=False
        ).exists()
        
        if exists:
            skipped_count += 1
            print(f'  跳过：{emp.name}（已在 Personnel 表中）')
            continue
        
        # 生成人员编号
        personnel_code = f'RY{emp.employee_code.replace("EMP", "")}'
        
        # 创建 Personnel 记录
        personnel = Personnel.objects.create(
            employee=emp,
            personnel_code=personnel_code,
            name=emp.name,
            gender=emp.gender,
            department='',  # 后续分配
            position='',    # 后续分配
            phone=emp.mobile,
            email=getattr(emp, 'email', None),
            entry_time=emp.entry_time,  # 使用入职时间作为入岗时间
            is_deleted=False,
            operator='system_import',
            remark=f'从 Employee 表导入，员工编号：{emp.employee_code}'
        )
        
        created_count += 1
        print(f'  ✓ 导入：{emp.name} -> {personnel_code}')
        
    except Exception as e:
        error_count += 1
        print(f'  ✗ 错误：{emp.name} - {str(e)}')

print('\n' + '=' * 80)
print(f'导入完成！')
print(f'  新增：{created_count} 人')
print(f'  跳过：{skipped_count} 人')
print(f'  错误：{error_count} 人')
print(f'\nPersonnel 表现在总记录数：{Personnel.objects.count()}')
print(f'Personnel 表未删除记录数：{Personnel.objects.filter(is_deleted=False).count()}')
print('=' * 80)
