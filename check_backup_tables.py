import sqlite3

backup_file = 'backup/eims_backup_20260411_103601.sqlite3'
conn = sqlite3.connect(backup_file)
cursor = conn.cursor()

# Check for department tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%department%' ORDER BY name")
dept_tables = cursor.fetchall()
print('Department tables:', [row[0] for row in dept_tables])

# Check for approval tables  
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%approval%' ORDER BY name")
approval_tables = cursor.fetchall()
print('Approval tables:', [row[0] for row in approval_tables])

# Check for role tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%role%' ORDER BY name")
role_tables = cursor.fetchall()
print('Role tables:', [row[0] for row in role_tables])

conn.close()
