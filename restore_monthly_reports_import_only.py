#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import monthly report data from exported JSON file to local database
从导出的JSON文件导入月度报告数据到本地数据库
"""

import os
import sys
import sqlite3
import json

EXPORT_FILE = r"e:\EIMS2026\monthly_report_export.json"
LOCAL_DB_PATH = r"e:\EIMS2026\db.sqlite3"


def import_data():
    """Import monthly report data to local database"""
    
    print("=" * 70)
    print("Importing Monthly Report Data")
    print("导入月度报告数据")
    print("=" * 70)
    print()
    
    # Check if export file exists
    if not os.path.exists(EXPORT_FILE):
        print(f"✗ Export file not found: {EXPORT_FILE}")
        print(f"✗ 导出文件不存在：{EXPORT_FILE}")
        print()
        print("Please run the export commands first:")
        print("请先运行导出命令：")
        print("1. ssh root@39.106.41.239 \"cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata eims_app.monthlyreport --indent 2 > /tmp/monthly_report_export.json\"")
        print("2. scp root@39.106.41.239:/tmp/monthly_report_export.json e:\\EIMS2026\\monthly_report_export.json")
        return False
    
    try:
        # Read the JSON file
        print(f"Reading export file: {EXPORT_FILE}")
        print(f"读取导出文件：{EXPORT_FILE}")
        
        # Try multiple encodings
        data = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(EXPORT_FILE, 'r', encoding=encoding) as f:
                    data = json.load(f)
                print(f"✓ Successfully read file with {encoding} encoding")
                print(f"✓ 使用 {encoding} 编码成功读取文件")
                break
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"  Trying {encoding} encoding... failed: {str(e)[:50]}")
                continue
        
        if data is None:
            print(f"✗ Failed to read file with any encoding")
            print(f"✗ 无法使用任何编码读取文件")
            return False
        
        print(f"✓ Found {len(data)} monthly report records")
        print(f"✓ 找到 {len(data)} 条月度报告记录")
        print()
        
        # Connect to local database
        print(f"Connecting to local database: {LOCAL_DB_PATH}")
        print(f"连接到本地数据库：{LOCAL_DB_PATH}")
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eims_app_monthlyreport'")
        if not cursor.fetchone():
            print("✗ Monthly report table does not exist in local database")
            print("✗ 本地数据库中不存在月度报告表")
            conn.close()
            return False
        
        print("✓ Database connection established")
        print("✓ 数据库连接已建立")
        print()
        
        # Auto-confirm for automated execution
        print("Auto-confirming import (automated mode)...")
        print("自动确认导入（自动化模式）...")
        print()
        
        # Clear existing data
        print("\nClearing existing monthly report data...")
        print("清除现有的月度报告数据...")
        cursor.execute("DELETE FROM eims_app_monthlyreport")
        print("✓ Existing data cleared")
        print("✓ 现有数据已清除")
        print()
        
        # Insert new data
        print("Inserting monthly report records...")
        print("插入月度报告记录...")
        inserted_count = 0
        error_count = 0
        
        for record in data:
            fields = record.get('fields', {})
            pk = record.get('pk')
            
            # Convert ForeignKey field names: add _id suffix
            # Django stores FK as fieldname_id in database
            db_fields = {}
            for key, value in fields.items():
                if key in ['reporter', 'project', 'approver']:
                    db_fields[key + '_id'] = value
                else:
                    db_fields[key] = value
            
            # Prepare INSERT statement
            columns = ['id'] + list(db_fields.keys())
            values = [pk] + list(db_fields.values())
            
            placeholders = ','.join(['?' for _ in values])
            column_names = ','.join(columns)
            
            try:
                cursor.execute(
                    f"INSERT OR REPLACE INTO eims_app_monthlyreport ({column_names}) VALUES ({placeholders})",
                    values
                )
                inserted_count += 1
                
                # Show progress every 10 records
                if inserted_count % 10 == 0:
                    print(f"  Progress: {inserted_count} records imported...")
                    print(f"  进度：已导入 {inserted_count} 条记录...")
                    
            except Exception as e:
                error_count += 1
                print(f"  Warning: Failed to insert record {pk}: {str(e)}")
                print(f"  警告：插入记录 {pk} 失败：{str(e)}")
        
        conn.commit()
        conn.close()
        
        print()
        print("=" * 70)
        print("Import Summary / 导入摘要")
        print("=" * 70)
        print(f"Total records in export: {len(data)}")
        print(f"导出文件中的总记录数：{len(data)}")
        print(f"Successfully imported: {inserted_count}")
        print(f"成功导入：{inserted_count}")
        print(f"Failed imports: {error_count}")
        print(f"导入失败：{error_count}")
        print("=" * 70)
        
        if error_count == 0:
            print("\n✓ All records imported successfully!")
            print("✓ 所有记录导入成功！")
        else:
            print(f"\n⚠ Import completed with {error_count} errors")
            print(f"⚠ 导入完成，但有 {error_count} 个错误")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during import: {str(e)}")
        print(f"✗ 导入过程中出错：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = import_data()
    
    if success:
        print("\n" + "=" * 70)
        print("Next Steps / 下一步")
        print("=" * 70)
        print("1. Restart your Django development server")
        print("   重启Django开发服务器")
        print("2. Navigate to the monthly report dashboard")
        print("   访问月度报告仪表板")
        print("3. Verify that all reports are displaying correctly")
        print("   验证所有报告显示正确")
        print("=" * 70)
    else:
        print("\n✗ Import failed. Please check the error messages above.")
        print("✗ 导入失败。请检查上面的错误信息。")
        sys.exit(1)
