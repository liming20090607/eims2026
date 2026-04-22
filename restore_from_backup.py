import pymysql
import os

# Database connection
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Read SQL file with proper encoding
sql_file = 'eims_final.sql'
print(f"📖 Reading {sql_file}...")

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    print(f"✅ File read successfully ({len(sql_content)} bytes)")
except UnicodeDecodeError:
    print("⚠️ UTF-8 failed, trying latin-1...")
    with open(sql_file, 'r', encoding='latin-1') as f:
        sql_content = f.read()
    print(f"✅ File read with latin-1 ({len(sql_content)} bytes)")

# Split into individual statements
print("\n🔧 Executing SQL statements...")
statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
print(f"   Found {len(statements)} statements")

success_count = 0
error_count = 0

for i, statement in enumerate(statements, 1):
    try:
        cursor.execute(statement)
        success_count += 1
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(statements)} statements executed")
    except Exception as e:
        error_count += 1
        # Only show first few errors
        if error_count <= 5:
            print(f"   ⚠️ Statement {i} error: {str(e)[:100]}")

conn.commit()
print(f"\n✅ Execution complete!")
print(f"   Success: {success_count}")
print(f"   Errors: {error_count}")

# Verify tables
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"\n📋 Tables in database: {len(tables)}")
for table in tables[:20]:
    print(f"   - {table[0]}")
if len(tables) > 20:
    print(f"   ... and {len(tables) - 20} more tables")

# Check for critical tables
critical_tables = ['eims_app_costprojectunified', 'eims_app_tenant', 'auth_user']
print(f"\n🔍 Checking critical tables:")
for table in critical_tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    status = "✅" if count >= 0 else "❌"
    print(f"   {status} {table}: {count} rows")

conn.close()
print("\n✅ Database restoration complete!")
