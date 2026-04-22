"""
Examine SQLite backup file to understand its schema and user data
"""
import sqlite3
import os

# Find the most recent backup
backup_dir = 'backup'
backups = [f for f in os.listdir(backup_dir) if f.endswith('.sqlite3')]
backups.sort(reverse=True)
latest_backup = os.path.join(backup_dir, backups[0])

print(f"Examining: {latest_backup}")
print(f"File size: {os.path.getsize(latest_backup) / 1024:.1f} KB\n")

# Connect to SQLite database
conn = sqlite3.connect(latest_backup)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print(f"Total tables: {len(tables)}\n")

# Check key tables
key_tables = [
    'auth_user',
    'auth_group', 
    'eims_app_userprofile',
    'eims_app_usertenantrelation',
    'eims_app_tenant',
]

for table_name in key_tables:
    try:
        # Check if table exists
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"Table: {table_name}")
        print(f"Records: {count}")
        
        if count > 0:
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {', '.join(columns)}")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            rows = cursor.fetchall()
            print(f"\nSample data:")
            for row in rows:
                print(f"  {row}")
    except Exception as e:
        print(f"  Error: {e}")

# Check for any tenant-related tables
print(f"\n{'='*60}")
print("Searching for tenant/company related tables...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%tenant%' OR name LIKE '%company%';")
tenant_tables = cursor.fetchall()
if tenant_tables:
    for table in tenant_tables:
        print(f"  Found: {table[0]}")
else:
    print("  No tenant/company tables found")

# Check for user group tables
print(f"\n{'='*60}")
print("Searching for user group related tables...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%group%';")
group_tables = cursor.fetchall()
if group_tables:
    for table in group_tables:
        print(f"  Found: {table[0]}")
else:
    print("  No group tables found")

conn.close()
print(f"\n{'='*60}")
print("Analysis complete!")
