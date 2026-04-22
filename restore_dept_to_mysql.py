"""
Script to restore department, role, and approval chain data from backup to MySQL
"""
import sqlite3
import os
from django.conf import settings
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

def get_backup_data(backup_db, table_name):
    """Extract all data from a specific table in backup SQLite database"""
    if not os.path.exists(backup_db):
        print(f"Error: Backup file not found: {backup_db}")
        return None
    
    conn = sqlite3.connect(backup_db)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        print(f"Warning: Table '{table_name}' not found in backup")
        conn.close()
        return None
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Get all data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"\n{table_name}:")
    print(f"  Columns: {len(columns)}")
    print(f"  Rows: {len(rows)}")
    
    return columns, rows

def restore_to_mysql(table_name, columns, rows):
    """Restore data from backup to MySQL database"""
    if not rows:
        print(f"  No data to restore for {table_name}")
        return 0
    
    db_alias = 'default'
    connection = connections[db_alias]
    cursor = connection.cursor()
    
    try:
        # Clear existing data
        print(f"  Clearing existing data from {table_name}...")
        cursor.execute(f"DELETE FROM {table_name}")
        
        # Prepare INSERT statement
        column_names = ', '.join([f"`{col}`" for col in columns])
        placeholders = ', '.join(['%s' for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        # Insert data in batches
        batch_size = 100
        restored = 0
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            cursor.executemany(insert_sql, batch)
            restored += len(batch)
            print(f"    Restored {restored}/{len(rows)} records...")
        
        connection.commit()
        print(f"  ✓ Successfully restored {restored} records to {table_name}")
        return restored
        
    except Exception as e:
        connection.rollback()
        print(f"  ✗ Error restoring {table_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        cursor.close()

def main():
    # Use recent backup (April 11, 2026) which has department management tables
    backup_file = 'backup/eims_backup_20260411_103601.sqlite3'
    
    print("="*80)
    print("Restoring Department Management Data from Backup to MySQL")
    print("="*80)
    print(f"Backup file: {backup_file}\n")
    
    # Tables to extract (using actual Django table names)
    tables_to_restore = [
        'eims_app_department',
        'eims_app_departmentrole', 
        'eims_app_approvalchain',
    ]
    
    total_restored = 0
    
    for table_name in tables_to_restore:
        result = get_backup_data(backup_file, table_name)
        if result:
            columns, rows = result
            count = restore_to_mysql(table_name, columns, rows)
            total_restored += count
    
    print("\n" + "="*80)
    print("RESTORATION COMPLETE")
    print("="*80)
    print(f"Total records restored: {total_restored}")
    print("\nPlease restart your Django server to see the changes.")

if __name__ == '__main__':
    main()
