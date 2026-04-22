"""
Multi-System Database Migration Script
Runs migrations on all four company databases.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command


def run_migrations():
    """Run migrations for all databases."""
    
    databases = [
        ('dingce', 'eims_dingce', '鼎策公司系统'),
        ('shengchang', 'eims_shengchang', '晟昌公司系统'),
        ('jiachengda', 'eims_jiachengda', '嘉诚达公司系统'),
        ('root_admin', 'eims_root', 'Root后台管理系统'),
    ]
    
    print("=" * 80)
    print("开始执行多系统数据库迁移...")
    print("=" * 80)
    
    for db_alias, db_name, description in databases:
        print(f"\n{'='*80}")
        print(f"迁移数据库: {description} ({db_name})")
        print(f"{'='*80}")
        
        try:
            # Run migrations for this database
            call_command('migrate', '--database', db_alias, verbosity=2)
            print(f"✓ {description} 迁移成功！")
        except Exception as e:
            print(f"✗ {description} 迁移失败: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("✓ 所有数据库迁移完成！")
    print("=" * 80)
    return True


if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
