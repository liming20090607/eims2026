"""
为 eims_root 数据库创建 costconsultingreminder 表
"""
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root123',
    database='eims_root'
)

cursor = conn.cursor()

sql = """
CREATE TABLE IF NOT EXISTS eims_app_costconsultingreminder (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT,
    project_id INT,
    sender_id INT,
    receiver_id INT NOT NULL,
    reminder_type VARCHAR(30) NOT NULL DEFAULT 'other',
    title VARCHAR(200) NOT NULL,
    content LONGTEXT NOT NULL,
    link_url VARCHAR(200) NOT NULL DEFAULT '',
    status VARCHAR(10) NOT NULL DEFAULT 'unread',
    snooze_until DATETIME(6),
    ignored_session VARCHAR(100) NOT NULL DEFAULT '',
    created_at DATETIME(6) NOT NULL,
    read_at DATETIME(6),
    INDEX eims_app_c_receiver_3a6c6e_idx (receiver_id),
    INDEX eims_app_c_tenant_id_4b0f52_idx (tenant_id),
    INDEX eims_app_c_status_8c9e8a_idx (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

try:
    cursor.execute(sql)
    conn.commit()
    print('✅ Table eims_app_costconsultingreminder created successfully')
except Exception as e:
    print(f'❌ Error: {e}')
finally:
    conn.close()
