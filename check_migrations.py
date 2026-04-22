import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root123', database='eims_jiachengda')
cursor = conn.cursor()
cursor.execute("SELECT app, name FROM django_migrations WHERE app IN ('auth', 'contenttypes', 'admin', 'sessions') ORDER BY id")
rows = cursor.fetchall()
print('Migration records:')
for r in rows:
    print(f'  {r[0]}.{r[1]}')
cursor.close()
conn.close()
