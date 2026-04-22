"""
Script to restore department, role, and approval chain data from backup
"""
import sqlite3
import os
import sys

def get_table_data(backup_db, table_name):
    """Extract all data from a specific table in backup database"""
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
    print(f"  Columns: {', '.join(columns)}")
    print(f"  Rows: {len(rows)}")
    
    return columns, rows

def main():
    # Use recent backup (April 11, 2026) which has department management tables
    backup_file = 'backup/eims_backup_20260411_103601.sqlite3'
    
    print("="*80)
    print("Restoring Department Management Data from Backup")
    print("="*80)
    print(f"Backup file: {backup_file}\n")
    
    # Tables to extract (using actual Django table names)
    tables_to_check = [
        'eims_app_department',
        'eims_app_departmentrole', 
        'eims_app_approvalchain',
        'eims_app_departmentmanager',
        'eims_app_approvalflowconfig',
    ]
    
    all_data = {}
    
    for table in tables_to_check:
        result = get_table_data(backup_file, table)
        if result:
            all_data[table] = result
    
    if not all_data:
        print("\nNo department-related data found in backup!")
        return
    
    # Display summary
    print("\n" + "="*80)
    print("DATA SUMMARY")
    print("="*80)
    for table, (columns, rows) in all_data.items():
        print(f"\n{table}: {len(rows)} records")
        if rows:
            print(f"  Sample data (first row):")
            for col, val in zip(columns[:5], rows[0][:5]):
                print(f"    {col}: {val}")
    
    print("\n" + "="*80)
    print("Ready to restore? (yes/no)")
    print("="*80)
    
    # Ask for confirmation
    response = input("\nEnter 'yes' to restore this data to current database: ").strip().lower()
    
    if response != 'yes':
        print("Restore cancelled.")
        return
    
    # Now restore to current database
    current_db = 'db.sqlite3'
    print(f"\nRestoring to: {current_db}")
    
    conn_backup = sqlite3.connect(backup_file)
    conn_current = sqlite3.connect(current_db)
    
    cursor_backup = conn_backup.cursor()
    cursor_current = conn_current.cursor()
    
    restored_count = 0
    
    for table, (columns, rows) in all_data.items():
        if not rows:
            continue
        
        print(f"\nRestoring {table}...")
        
        # Clear existing data
        cursor_current.execute(f"DELETE FROM {table}")
        
        # Insert backup data
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        try:
            cursor_current.executemany(
                f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})",
                rows
            )
            restored_count += len(rows)
            print(f"  ✓ Restored {len(rows)} records")
        except Exception as e:
            print(f"  ✗ Error restoring {table}: {e}")
    
    conn_current.commit()
    conn_backup.close()
    conn_current.close()
    
    print("\n" + "="*80)
    print(f"RESTORATION COMPLETE")
    print("="*80)
    print(f"Total records restored: {restored_count}")
    print("\nPlease restart your Django server to see the changes.")

if __name__ == '__main__':
    main()
