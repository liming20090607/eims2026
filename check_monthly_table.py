import sqlite3
import sys

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eims_app_monthlyreport'")
table = cursor.fetchone()

if table:
    print("✓ Table 'eims_app_monthlyreport' exists")
    cursor.execute("SELECT COUNT(*) FROM eims_app_monthlyreport")
    count = cursor.fetchone()[0]
    print(f"  Current records: {count}")
else:
    print("✗ Table 'eims_app_monthlyreport' does NOT exist")
    print("  Need to run migrations first")

conn.close()
