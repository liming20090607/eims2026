import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

for db_name in ['dingce', 'shengchang', 'jiachengda']:
    cursor = connections[db_name].cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    eims_tables = [t for t in tables if t.startswith('eims_app_')]
    print(f"{db_name}: {len(eims_tables)} tables")
    
    # Check important tables
    important = ['eims_app_employee', 'eims_app_projectdetail', 'eims_app_contract']
    for table in important:
        status = "OK" if table in tables else "MISSING"
        print(f"  - {table}: {status}")
