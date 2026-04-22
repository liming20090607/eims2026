import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from eims_app.models import Employee
emp = Employee.objects.filter(personnel_code='DCRY-010').first()
if emp:
    print(f'DCRY-010 已存在: {emp.name} | ID:{emp.id} | tenant:{emp.tenant_id}')
else:
    print('DCRY-010 不存在')
