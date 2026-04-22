import pymysql
from datetime import datetime

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Insert tenants with ALL required fields
tenants = [
    ('dingce', '鼎策工程咨询', '鼎策', '', '', '', '', '', '', '', '', 1, now, now),
    ('shengchang', '晟昌工程科技', '晟昌', '', '', '', '', '', '', '', '', 1, now, now),
    ('jiachengda', '嘉诚达造价咨询', '嘉诚达', '', '', '', '', '', '', '', '', 1, now, now),
    ('root_admin', 'Root管理后台', 'Root', '', '', '', '', '', '', '', '', 1, now, now),
]

for t in tenants:
    try:
        cursor.execute(
            """INSERT INTO eims_app_tenant 
               (code, name, short_name, logo, contact_person, contact_phone, 
                contact_email, address, project_code_prefix, description, remark, 
                is_active, create_time, update_time) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE name=VALUES(name)
            """,
            t
        )
        print(f"✅ Tenant created: {t[1]} ({t[0]})")
    except Exception as e:
        print(f"❌ Failed {t[0]}: {e}")

conn.commit()

# Verify
cursor.execute("SELECT id, code, name, is_active FROM eims_app_tenant")
tenants_list = cursor.fetchall()
print(f"\n📋 Tenants in database: {len(tenants_list)}")
for t in tenants_list:
    print(f"   ID={t[0]}, code={t[1]}, name={t[2]}, active={t[3]}")

conn.close()

if len(tenants_list) >= 4:
    print("\n✅ SUCCESS! All 4 tenants created")
else:
    print(f"\n⚠️ WARNING: Only {len(tenants_list)} tenants found")
