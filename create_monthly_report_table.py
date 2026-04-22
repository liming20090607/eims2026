import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Create the monthly report table
create_table_sql = """
CREATE TABLE IF NOT EXISTS eims_app_monthlyreport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    project_code VARCHAR(50) NOT NULL,
    report_year INTEGER NOT NULL,
    report_month VARCHAR(7) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    project_progress TEXT NOT NULL DEFAULT '',
    current_status VARCHAR(20) NOT NULL DEFAULT '',
    last_month_cumulative_output DECIMAL(15,2) NOT NULL DEFAULT 0,
    monthly_output_value DECIMAL(15,2) NOT NULL DEFAULT 0,
    current_cumulative_output DECIMAL(15,2) NOT NULL DEFAULT 0,
    last_month_cumulative_payment DECIMAL(15,2) NOT NULL DEFAULT 0,
    monthly_payment DECIMAL(15,2) NOT NULL DEFAULT 0,
    current_cumulative_payment DECIMAL(15,2) NOT NULL DEFAULT 0,
    payment_description TEXT NOT NULL DEFAULT '',
    personnel_changes TEXT NOT NULL DEFAULT '',
    total_personnel INTEGER NOT NULL DEFAULT 0,
    current_payment_request DECIMAL(15,2) NOT NULL DEFAULT 0,
    payment_progress VARCHAR(200) NOT NULL DEFAULT '',
    payment_issues TEXT NOT NULL DEFAULT '',
    next_month_plan_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    next_month_plan_detail TEXT NOT NULL DEFAULT '',
    next_month_assistance TEXT NOT NULL DEFAULT '',
    should_submit_date DATE,
    actual_submit_date DATE,
    submit_time DATETIME,
    approve_time DATETIME,
    approver_id INTEGER,
    reject_reason TEXT NOT NULL DEFAULT '',
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    FOREIGN KEY (reporter_id) REFERENCES auth_user(id),
    FOREIGN KEY (project_id) REFERENCES eims_app_projectdetail(id),
    FOREIGN KEY (approver_id) REFERENCES auth_user(id)
);

CREATE INDEX IF NOT EXISTS eims_app_monthlyreport_project_code ON eims_app_monthlyreport(project_code);
CREATE INDEX IF NOT EXISTS eims_app_monthlyreport_report_year_month ON eims_app_monthlyreport(report_year, report_month);
CREATE INDEX IF NOT EXISTS eims_app_monthlyreport_status ON eims_app_monthlyreport(status);
CREATE UNIQUE INDEX IF NOT EXISTS eims_app_monthlyreport_unique ON eims_app_monthlyreport(project_id, report_year, report_month);
"""

try:
    cursor.executescript(create_table_sql)
    conn.commit()
    print("✓ Table 'eims_app_monthlyreport' created successfully")
    
    # Verify table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eims_app_monthlyreport'")
    if cursor.fetchone():
        print("✓ Table verification passed")
    else:
        print("✗ Table verification failed")
        
except Exception as e:
    print(f"✗ Error creating table: {e}")
finally:
    conn.close()
