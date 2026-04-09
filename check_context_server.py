import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from eims_app.context_processors import sidebar_context
from eims_app.models.model_tenant import Tenant

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()

if admin:
    factory = RequestFactory()
    request = factory.get('/')
    request.user = admin
    request.session = {'tenant_id': 1, 'sidebar_collapsed': False}
    request.tenant = Tenant.objects.get(id=1)
    
    ctx = sidebar_context(request)
    tenants = ctx.get('tenants_all', [])
    
    print('=== Context Processor 测试结果 ===')
    print(f'Type: {type(tenants)}')
    
    # Force evaluate
    tenant_list = list(tenants) if hasattr(tenants, '__iter__') else tenants
    print(f'Count: {len(tenant_list)}')
    
    for t in tenant_list:
        print(f'  - {t.name} (id={t.id})')
else:
    print('No superuser found')
