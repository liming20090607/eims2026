"""
EIMS Cloud Server Sync Script
Pull latest code from Gitee and import MySQL data
"""
import os
import sys

print("=" * 60)
print("EIMS Cloud Server Sync Tool")
print("=" * 60)

# Step 1: Pull latest code
print("\n[1/4] Pulling latest code from Gitee...")
os.system("cd /var/www/eims && git fetch --all")
os.system("cd /var/www/eims && git reset --hard gitee/master")
os.system("cd /var/www/eims && git clean -fd")
print("[OK] Code updated from Gitee")

# Step 2: Import MySQL database
print("\n[2/4] Importing MySQL database...")
sql_file = "/var/www/eims/eims_mysql_backup.sql"

if os.path.exists(sql_file):
    os.system("mysql -u root -proot123 -e 'DROP DATABASE IF EXISTS eims;'")
    os.system("mysql -u root -proot123 -e 'CREATE DATABASE eims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'")
    os.system(f"mysql -u root -proot123 eims < {sql_file}")
    print("[OK] Database imported successfully")
else:
    print(f"[ERROR] SQL file not found: {sql_file}")
    sys.exit(1)

# Step 3: Run Django migrations
print("\n[3/4] Running Django migrations...")
os.system("cd /var/www/eims && python3 manage.py migrate --settings=settings_local_mysql")
print("[OK] Migrations completed")

# Step 4: Collect static files
print("\n[4/4] Collecting static files...")
os.system("cd /var/www/eims && python3 manage.py collectstatic --noinput --settings=settings_local_mysql")
print("[OK] Static files collected")

print("\n" + "=" * 60)
print("Sync Complete!")
print("=" * 60)
print("\nPlease restart your services:")
print("  1. sudo systemctl restart gunicorn")
print("  2. sudo systemctl restart nginx")
print("\nAccess: http://39.106.41.239")
