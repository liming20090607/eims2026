import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from eims_app.models import Employee
emps = Employee.objects.filter(tenant_id=2, is_deleted=False).order_by('id')
print(f'鼎策公司 (tenant_id=2) 共有 {emps.count()} 名员工:')
for e in emps:
    print(f'  ID:{e.id} | {e.personnel_code} | {e.name}')
