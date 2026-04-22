#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从云服务器导出月度报告数据并导入本地数据库
Export Monthly Report data from cloud server and import to local database
"""

import os
import sys
import sqlite3
import subprocess
from datetime import datetime

# Configuration
CLOUD_SERVER = "root@39.106.41.239"
CLOUD_DB_PATH = "/var/www/eims/db.sqlite3"
LOCAL_DB_PATH = r"e:\EIMS2026\db.sqlite3"
EXPORT_FILE = r"e:\EIMS2026\monthly_report_export.json"

def export_from_cloud():
    """Export monthly report data from cloud server"""
    print("=" * 70)
    print("Step 1: Exporting Monthly Report data from cloud server...")
    print("=" * 70)
    
    # Create Django management command to export data
    export_command = f'''ssh {CLOUD_SERVER} "cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata eims_app.monthlyreport --indent 2 > /tmp/monthly_report_export.json && echo 'EXPORT_SUCCESS' && wc -l /tmp/monthly_report.json"'''
    
    print(f"Executing: {export_command}")
    print("\nPlease enter your SSH password when prompted...\n")
    
    try:
        result = subprocess.run(export_command, shell=True, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✓ Export command executed successfully")
            
            # Download the exported file
            print("\nDownloading exported file from server...")
            download_command = f"scp {CLOUD_SERVER}:/tmp/monthly_report_export.json {EXPORT_FILE}"
            download_result = subprocess.run(download_command, shell=True, capture_output=False, text=True)
            
            if download_result.returncode == 0:
                print(f"✓ File downloaded to: {EXPORT_FILE}")
                return True
            else:
                print("✗ Failed to download file")
                return False
        else:
            print("✗ Export command failed")
            return False
            
    except Exception as e:
        print(f"✗ Error during export: {str(e)}")
        return False


def import_to_local():
    """Import monthly report data to local database"""
    print("\n" + "=" * 70)
    print("Step 2: Importing Monthly Report data to local database...")
    print("=" * 70)
    
    if not os.path.exists(EXPORT_FILE):
        print(f"✗ Export file not found: {EXPORT_FILE}")
        return False
    
    try:
        # Read the JSON file
        with open(EXPORT_FILE, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
        
        print(f"Found {len(data)} monthly report records in export file")
        
        # Connect to local database
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eims_app_monthlyreport'")
        if not cursor.fetchone():
            print("✗ Monthly report table does not exist in local database")
            conn.close()
            return False
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("\nClearing existing monthly report data...")
        cursor.execute("DELETE FROM eims_app_monthlyreport")
        
        # Insert new data
        print("Inserting monthly report records...")
        inserted_count = 0
        
        for record in data:
            fields = record.get('fields', {})
            pk = record.get('pk')
            
            # Prepare INSERT statement
            columns = ['id'] + list(fields.keys())
            values = [pk] + list(fields.values())
            
            placeholders = ','.join(['?' for _ in values])
            column_names = ','.join(columns)
            
            try:
                cursor.execute(
                    f"INSERT OR REPLACE INTO eims_app_monthlyreport ({column_names}) VALUES ({placeholders})",
                    values
                )
                inserted_count += 1
            except Exception as e:
                print(f"Warning: Failed to insert record {pk}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✓ Successfully imported {inserted_count} monthly report records")
        return True
        
    except Exception as e:
        print(f"✗ Error during import: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_import():
    """Verify the imported data"""
    print("\n" + "=" * 70)
    print("Step 3: Verifying imported data...")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM eims_app_monthlyreport")
        total_count = cursor.fetchone()[0]
        
        # Count by status
        cursor.execute("SELECT status, COUNT(*) FROM eims_app_monthlyreport GROUP BY status")
        status_counts = cursor.fetchall()
        
        # Get recent records
        cursor.execute("""
            SELECT id, project_id, report_year, report_month, status, created_at 
            FROM eims_app_monthlyreport 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_records = cursor.fetchall()
        
        conn.close()
        
        print(f"\nTotal monthly reports: {total_count}")
        print("\nRecords by status:")
        for status, count in status_counts:
            print(f"  - {status}: {count}")
        
        print("\n5 most recent records:")
        for record in recent_records:
            print(f"  ID: {record[0]}, Project: {record[1]}, Period: {record[2]}-{record[3]}, Status: {record[4]}")
        
        print("\n✓ Verification complete")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {str(e)}")
        return False


def main():
    print("\n" + "=" * 70)
    print("Monthly Report Data Recovery Tool")
    print("从云服务器恢复月度报告数据")
    print("=" * 70)
    print(f"\nCloud Server: {CLOUD_SERVER}")
    print(f"Local Database: {LOCAL_DB_PATH}")
    print(f"Export File: {EXPORT_FILE}")
    print("\n" + "=" * 70)
    
    # Step 1: Export from cloud
    if not export_from_cloud():
        print("\n✗ Export failed. Please check your SSH connection and try again.")
        sys.exit(1)
    
    # Step 2: Import to local
    if not import_to_local():
        print("\n✗ Import failed. Please check the error messages above.")
        sys.exit(1)
    
    # Step 3: Verify
    if not verify_import():
        print("\n⚠ Verification encountered issues, but data may still be valid.")
    
    print("\n" + "=" * 70)
    print("✓ Monthly Report data recovery completed successfully!")
    print("✓ 月度报告数据恢复完成！")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart your Django development server")
    print("2. Navigate to the monthly report dashboard")
    print("3. Verify that all reports are displaying correctly")
    print("\n重启Django开发服务器，然后访问月报仪表板验证数据。")


if __name__ == "__main__":
    main()
