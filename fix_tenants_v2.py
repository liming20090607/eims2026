import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Get all columns in tenant table
cursor.execute("""
    SELECT COLUMN_NAME, COLUMN_DEFAULT, IS_NULLABLE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'eims2026_dev' 
    AND TABLE_NAME = 'eims_app_tenant'
    ORDER BY ORDINAL_POSITION
""")
columns = cursor.fetchall()
print("📋 Tenant table columns:")
for col in columns:
    print(f"   {col[0]}: default={col[1]}, nullable={col[2]}")

# Now insert tenants with all fields
tenants = [
    ('dingce', '鼎策工程咨询', '鼎策', '', '', '', '', '', '', 1),
    ('shengchang', '晟昌工程科技', '晟昌', '', '', '', '', '', '', 1),
    ('jiachengda', '嘉诚达造价咨询', '嘉诚达', '', '', '', '', '', '', 1),
    ('root_admin', 'Root管理后台', 'Root', '', '', '', '', '', '', 1),
]

for tenant_data in tenants:
    try:
        cursor.execute(
            """INSERT INTO eims_app_tenant 
               (code, name, short_name, project_code_prefix, description, 
                contact_person, contact_phone, contact_email, logo, is_active) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
               ON DUPLICATE KEY UPDATE name=VALUES(name)
            """,
            tenant_data
        )
        print(f"✅ Tenant: {tenant_data[1]}")
    except Exception as e:
        print(f"⚠️ {tenant_data[0]}: {e}")
        # Try to see what's failing
        cursor.execute("DESCRIBE eims_app_tenant")
        for col in cursor.fetchall():
            print(f"   {col}")
        break

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
