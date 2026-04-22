import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=" * 70)
print("Monthly Report Data Verification")
print("月度报告数据验证")
print("=" * 70)

# Count total records
cursor.execute("SELECT COUNT(*) FROM eims_app_monthlyreport")
total_count = cursor.fetchone()[0]
print(f"\nTotal records: {total_count}")
print(f"总记录数：{total_count}")

if total_count > 0:
    # Get all records
    cursor.execute("""
        SELECT id, project_id, report_year, report_month, status, 
               monthly_output_value, current_cumulative_output
        FROM eims_app_monthlyreport
        ORDER BY report_year DESC, report_month DESC
    """)
    
    print("\n" + "-" * 70)
    print("Report Details / 报告详情:")
    print("-" * 70)
    
    for row in cursor.fetchall():
        print(f"\nID: {row[0]}")
        print(f"Project ID: {row[1]}")
        print(f"Year: {row[2]}, Month: {row[3]}")
        print(f"Status: {row[4]}")
        print(f"Monthly Output: {row[5]}万元")
        print(f"Cumulative Output: {row[6]}万元")
        print("-" * 70)

conn.close()

print("\n✓ Verification complete!")
print("✓ 验证完成！")
