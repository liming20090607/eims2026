import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root123', database='eims_root')
cursor = conn.cursor()

# Check if django_migrations table exists
cursor.execute("SHOW TABLES LIKE 'django_migrations'")
if cursor.fetchone():
    print("django_migrations table exists")
    cursor.execute("SELECT COUNT(*) FROM django_migrations")
    count = cursor.fetchone()[0]
    print(f"Number of migration records: {count}")
    
    # Delete all migration records
    cursor.execute("DELETE FROM django_migrations")
    conn.commit()
    print("All migration records deleted")
else:
    print("django_migrations table does not exist")

# Drop all tables to start fresh
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"\nDropping {len(tables)} tables...")
for table in tables:
    table_name = table[0]
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
    print(f"  - Dropped {table_name}")

conn.commit()
cursor.close()
conn.close()
print("\n✓ Database eims_root cleared successfully!")
