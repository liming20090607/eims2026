import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT id, personnel_code, name FROM eims_app_employee WHERE personnel_code LIKE 'JCDRY-%' ORDER BY CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)")
rows = cursor.fetchall()

print('JCDRY codes in Employee table:')
print('-' * 50)
for r in rows:
    print(f'{r[0]:3} | {r[1]:15} | {r[2]}')
