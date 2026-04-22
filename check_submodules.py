import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_sub_module import SubModule
from eims_app.models.model_tenant_module import TenantModule

print('=== 一级模块 ===')
for m in TenantModule.objects.all():
    print(f'{m.id}: {m.name} ({m.code})')

print('\n=== 子模块 ===')
for s in SubModule.objects.all().order_by('parent_module__sort_order', 'sort_order'):
    print(f'{s.id}: {s.parent_module.name} - {s.name} ({s.code}) 启用:{s.is_active}')

print(f'\n总计: {SubModule.objects.count()} 个子模块')
