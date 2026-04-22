import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute('DESCRIBE eims_app_employee')
cols = cursor.fetchall()

print("Employee Table Columns:")
print("-" * 60)
for c in cols:
    print(f"{c[0]:20} {c[1]:20} {'NULL' if c[2]=='YES' else 'NOT NULL':10}")
