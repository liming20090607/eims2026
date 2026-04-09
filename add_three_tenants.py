#!/usr/bin/env python3
"""
添加三个公司到 MySQL 数据库
"""
import os
import sys

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')

import django
django.setup()

from eims_app.models.model_tenant import Tenant

print("=" * 60)
print("添加三个公司到 MySQL 数据库")
print("=" * 60)

companies = [
    {'code': 'COMPANY_A', 'name': '广西鼎策工程顾问有限责任公司', 'short_name': '鼎策工程'},
    {'code': 'COMPANY_B', 'name': '广西晟昌工程科技有限责任公司', 'short_name': '晟昌科技'},
    {'code': 'COMPANY_C', 'name': '广西嘉诚达工程造价咨询有限公司', 'short_name': '嘉诚达'},
]

for company in companies:
    tenant, created = Tenant.objects.get_or_create(
        code=company['code'],
        defaults={
            'name': company['name'],
            'short_name': company['short_name'],
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ 新增: {company['name']} (ID={tenant.id})")
    else:
        print(f"⏭️  已存在: {company['name']} (ID={tenant.id})")

print()
print("=" * 60)
print("当前所有公司:")
print("=" * 60)
tenants = Tenant.objects.all()
for t in tenants:
    print(f"  ID={t.id}, Code={t.code}, Name={t.name}, Active={t.is_active}")

print("\n✅ 完成！")
