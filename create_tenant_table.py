import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Create tenant table
print("Creating eims_app_tenant table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS eims_app_tenant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    short_name VARCHAR(50) DEFAULT '',
    logo VARCHAR(255) DEFAULT '',
    contact_person VARCHAR(100) DEFAULT '',
    contact_phone VARCHAR(20) DEFAULT '',
    contact_email VARCHAR(100) DEFAULT '',
    address TEXT,
    project_code_prefix VARCHAR(50) DEFAULT '',
    description TEXT,
    remark TEXT,
    is_active TINYINT(1) DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""")

print("✅ Tenant table created")

# Insert default tenants
tenants = [
    ('dingce', '鼎策工程咨询', '鼎策'),
    ('shengchang', '晟昌工程科技', '晟昌'),
    ('jiachengda', '嘉诚达造价咨询', '嘉诚达'),
    ('root_admin', 'Root管理后台', 'Root'),
]

for code, name, short_name in tenants:
    cursor.execute("""
        INSERT INTO eims_app_tenant (code, name, short_name, is_active) 
        VALUES (%s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE name=VALUES(name), short_name=VALUES(short_name)
    """, (code, name, short_name))
    print(f"✅ Tenant created: {name} ({code})")

conn.commit()

# Verify
cursor.execute("SELECT id, code, name, is_active FROM eims_app_tenant")
tenants_list = cursor.fetchall()
print(f"\n📋 Total tenants: {len(tenants_list)}")
for t in tenants_list:
    print(f"   ID={t[0]}, code={t[1]}, name={t[2]}, active={t[3]}")

conn.close()
print("\n✅ Tenant setup complete!")
