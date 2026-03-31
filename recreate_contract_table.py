import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 创建 Contract 表（简化版，只包含必要字段）
cursor.execute('''
CREATE TABLE IF NOT EXISTS eims_app_Contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_code VARCHAR(50) NOT NULL UNIQUE,
    project_code VARCHAR(50) NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    contract_type VARCHAR(50),
    status VARCHAR(50),
    contract_amount DECIMAL(15,2),
    project_investment DECIMAL(15,2),
    contract_party_a VARCHAR(200),
    contract_party_b VARCHAR(200),
    signing_time DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
print("✓ Contract 表已重新创建")

# 验证表是否存在
cursor.execute("SELECT COUNT(*) FROM eims_app_Contract")
count = cursor.fetchone()[0]
print(f"✓ Contract 表现有 {count} 条记录")

conn.close()
