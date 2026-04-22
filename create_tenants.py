import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Add short_name column if not exists
try:
    cursor.execute("ALTER TABLE eims_app_tenant ADD COLUMN short_name VARCHAR(50) DEFAULT '' AFTER name")
    print("✅ Added short_name column")
except Exception as e:
    if 'Duplicate column name' not in str(e):
        print(f"⚠️ {e}")

# Insert tenants
tenants = [
    ('dingce', '鼎策工程咨询', '鼎策', 1),
    ('shengchang', '晟昌工程科技', '晟昌', 1),
    ('jiachengda', '嘉诚达造价咨询', '嘉诚达', 1),
    ('root_admin', 'Root管理后台', 'Root', 1),
]

for code, name, short_name, is_active in tenants:
    try:
        cursor.execute(
            "INSERT INTO eims_app_tenant (code, name, short_name, is_active) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name), short_name=VALUES(short_name)",
            (code, name, short_name, is_active)
        )
        print(f"✅ Tenant created: {name} ({code})")
    except Exception as e:
        print(f"⚠️ {code}: {e}")

conn.commit()
cursor.execute("SELECT id, code, name, is_active FROM eims_app_tenant")
print("\n📋 Current tenants:")
for row in cursor.fetchall():
    print(f"   {row}")

conn.close()
print("\n✅ Done!")
