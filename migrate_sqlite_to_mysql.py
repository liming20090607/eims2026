"""
EIMS Data Migration Script - SQLite to MySQL
"""
import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from django.db import connection
from django.core.management import call_command

print("=" * 60)
print("EIMS Data Migration Tool - SQLite to MySQL")
print("=" * 60)

# Step 1: Check SQLite tables
print("\n[1/4] Analyzing SQLite database...")
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
sqlite_tables = [row[0] for row in cursor.fetchall()]
print(f"  Found {len(sqlite_tables)} tables in SQLite")

# Step 2: Export data from SQLite
print("\n[2/4] Exporting data from SQLite...")
sqlite_data_file = os.path.join(project_root, 'sqlite_backup.json')

try:
    with open(sqlite_data_file, 'w', encoding='utf-8') as f:
        # Export all data, excluding problematic tables
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent=2',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            stdout=f
        )
    
    file_size = os.path.getsize(sqlite_data_file)
    file_size_mb = file_size / (1024 * 1024)
    print(f"  Export successful!")
    print(f"  File: {sqlite_data_file}")
    print(f"  Size: {file_size_mb:.2f} MB")
    
except Exception as e:
    print(f"  Export failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Read the data
print("\n[3/4] Processing exported data...")
try:
    with open(sqlite_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter out contenttypes and permissions
    filtered_data = [
        item for item in data
        if not item['model'].startswith('contenttypes')
        and not item['model'].startswith('auth.permission')
    ]
    
    print(f"  Total records: {len(data)}")
    print(f"  After filtering: {len(filtered_data)}")
    
    # Count by model
    model_counts = {}
    for item in filtered_data:
        model = item['model']
        model_counts[model] = model_counts.get(model, 0) + 1
    
    print("\n  Data summary:")
    for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {model}: {count} records")
        
except Exception as e:
    print(f"  Processing failed: {e}")
    sys.exit(1)

# Step 4: Ask for confirmation
print("\n" + "=" * 60)
confirm = input("Proceed to import data into MySQL? (y/n): ")
if confirm.lower() != 'y':
    print("Migration cancelled.")
    sys.exit(0)

print("\n[4/4] Importing data into MySQL...")
print("  This may take a while...")

try:
    # Switch to MySQL settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_local_mysql'
    
    # Reload Django with MySQL settings
    from django.conf import settings
    settings._wrapped = None
    
    # Import MySQL settings
    import settings_local_mysql
    from settings_local_mysql import *
    
    # Reload Django setup
    django.setup()
    
    # Load data into MySQL
    with open(sqlite_data_file, 'r', encoding='utf-8') as f:
        call_command('loaddata', sqlite_data_file, verbosity=2)
    
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\nMigration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
