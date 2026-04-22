"""Check tables in company databases"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

databases = ['default', 'dingce', 'shengchang', 'jiachengda', 'root_admin']

for db_name in databases:
    try:
        cursor = connections[db_name].cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n{db_name} ({len(tables)} tables):")
        
        # Check for key tables
        key_tables = ['eims_app_userprofile', 'eims_app_usertenantrelation', 'eims_app_tenant']
        for key_table in key_tables:
            if key_table in tables:
                print(f"  ✓ {key_table}")
            else:
                print(f"  ✗ {key_table} MISSING")
        
        # Show total count
        if len(tables) <= 20:
            for table in sorted(tables):
                if table not in key_tables:
                    print(f"  - {table}")
                    
    except Exception as e:
        print(f"\n{db_name}: ERROR - {e}")
