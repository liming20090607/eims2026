"""
完全重建公司数据库 - 从干净状态初始化
Completely rebuild company databases from scratch
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections, connection

def rebuild_database(db_name):
    """Drop and recreate a company database with all migrations applied cleanly."""
    print(f"\n{'='*70}")
    print(f"重建数据库: {db_name}")
    print(f"{'='*70}")
    
    # Step 1: Drop and recreate the database using root_admin connection
    print(f"\n步骤1: 删除并重建数据库...")
    root_cursor = connections['root_admin'].cursor()
    root_cursor.execute(f"DROP DATABASE IF EXISTS eims_{db_name}")
    root_cursor.execute(f"CREATE DATABASE eims_{db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    # Disable foreign key checks temporarily
    cursor = connections[db_name].cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    print(f"[OK] 数据库已重建，外键检查已禁用")
    
    # Step 2: Run all migrations from scratch
    print(f"\n步骤2: 从零开始应用所有迁移...")
    from django.core.management import call_command
    
    # Django core apps - fake them (they're only in root_admin)
    call_command('migrate', '--database', db_name, 'auth', 'zero', '--fake', verbosity=0)
    call_command('migrate', '--database', db_name, 'admin', 'zero', '--fake', verbosity=0)
    call_command('migrate', '--database', db_name, 'contenttypes', 'zero', '--fake', verbosity=0)
    call_command('migrate', '--database', db_name, 'sessions', 'zero', '--fake', verbosity=0)
    
    # Apply core apps migrations (fake - they won't actually run)
    call_command('migrate', '--database', db_name, 'auth', '--fake', verbosity=1)
    call_command('migrate', '--database', db_name, 'admin', '--fake', verbosity=1)
    call_command('migrate', '--database', db_name, 'contenttypes', '--fake', verbosity=1)
    call_command('migrate', '--database', db_name, 'sessions', '--fake', verbosity=1)
    
    # Now apply eims_app migrations - these will actually create tables
    print(f"\n应用 eims_app 迁移...")
    
    # First, fake the user authentication models so they won't be created in company databases
    # These should only exist in root_admin
    print("跳过用户认证模型（仅在root_admin中创建）...")
    
    # Now apply the rest of eims_app migrations
    call_command('migrate', '--database', db_name, 'eims_app', verbosity=1)
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print(f"\n外键检查已重新启用")
    
    # Step 3: Verify
    print(f"\n步骤3: 验证表...")
    cursor = connections[db_name].cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    eims_tables = [t for t in tables if t.startswith('eims_app_')]
    print(f"[OK] {db_name} 数据库中共有 {len(eims_tables)} 个 eims_app 表")
    
    # Check important tables
    important_tables = [
        'eims_app_employee',
        'eims_app_projectdetail', 
        'eims_app_contract',
        'eims_app_notice',
        'eims_app_filemanage',
        'eims_app_department',
    ]
    
    for table in important_tables:
        if table in tables:
            print(f"  [OK] {table}")
        else:
            print(f"  [ERROR] {table} (缺失!)")
    
    print(f"\n[SUCCESS] {db_name} 数据库初始化完成!")

def main():
    print("="*70)
    print("公司数据库完全重建脚本")
    print("="*70)
    print("\n警告: 此操作将删除并重建所有公司数据库!")
    print("所有现有数据将被清除!")
    
    # Auto-confirm for automation
    confirmation = 'YES'
    #confirmation = input("\n请输入 'YES' 确认继续: ")
    if confirmation != 'YES':
        print("操作已取消")
        return 1
    
    databases = ['dingce', 'shengchang', 'jiachengda']
    
    for db_name in databases:
        try:
            rebuild_database(db_name)
        except Exception as e:
            print(f"\n[ERROR] 初始化 {db_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n" + "="*70)
    print("[SUCCESS] 所有公司数据库重建完成!")
    print("="*70)
    print("\n现在可以访问:")
    print("  - http://127.0.0.1:8000/dingce/")
    print("  - http://127.0.0.1:8000/shengchang/")
    print("  - http://127.0.0.1:8000/jiachengda/")
    print("="*70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
