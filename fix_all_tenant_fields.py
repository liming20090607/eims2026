import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Add all missing columns
missing_columns = [
    ("short_name", "VARCHAR(50) DEFAULT '' AFTER name"),
    ("project_code_prefix", "VARCHAR(50) DEFAULT '' AFTER is_active"),
    ("description", "TEXT AFTER project_code_prefix"),
    ("contact_person", "VARCHAR(100) DEFAULT '' AFTER description"),
    ("contact_phone", "VARCHAR(20) DEFAULT '' AFTER contact_person"),
    ("contact_email", "VARCHAR(100) DEFAULT '' AFTER contact_phone"),
    ("logo", "VARCHAR(255) DEFAULT '' AFTER contact_email"),
    ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP AFTER logo"),
    ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at"),
]

for col_name, col_def in missing_columns:
    try:
        cursor.execute(f"ALTER TABLE eims_app_tenant ADD COLUMN {col_name} {col_def}")
        print(f"✅ Added {col_name}")
    except Exception as e:
        if 'Duplicate column name' in str(e):
            print(f"ℹ️ {col_name} already exists")
        else:
            print(f"⚠️ {col_name}: {e}")

conn.commit()

# Now insert tenants
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
        print(f"✅ Tenant: {name}")
    except Exception as e:
        print(f"⚠️ {code}: {e}")

conn.commit()

# Verify
cursor.execute("SELECT id, code, name, is_active FROM eims_app_tenant")
tenants_list = cursor.fetchall()
print(f"\n📋 Tenants in database: {len(tenants_list)}")
for t in tenants_list:
    print(f"   {t}")

conn.close()

if len(tenants_list) >= 4:
    print("\n✅ SUCCESS! All tenants created")
else:
    print("\n⚠️ WARNING: Some tenants missing")
