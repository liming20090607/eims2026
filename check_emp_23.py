import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from eims_app.models import Employee
emp = Employee.objects.get(id=23)
print(f'ID: {emp.id}')
print(f'人员编号: {emp.personnel_code}')
print(f'姓名: {emp.name}')
print(f'tenant_id: {emp.tenant_id}')
print(f'tenant: {emp.tenant}')
print(f'is_deleted: {emp.is_deleted}')
