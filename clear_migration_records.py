import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root123', database='eims_jiachengda')
cursor = conn.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app IN ('auth', 'contenttypes', 'admin', 'sessions')")
conn.commit()
print(f'Deleted {cursor.rowcount} migration records')
cursor.close()
conn.close()
