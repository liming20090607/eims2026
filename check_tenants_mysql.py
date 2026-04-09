#!/usr/bin/env python3
"""
Check Tenant data in MySQL database
"""
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')

import django
django.setup()

from eims_app.models.model_tenant import Tenant

print("=== MySQL 数据库中的 Tenant 数据 ===")
tenants = Tenant.objects.all()
print(f"总记录数: {tenants.count()}")
print()

for t in tenants:
    print(f"  ID={t.id}, Name={t.name}, Code={t.code}, Active={t.is_active}")
