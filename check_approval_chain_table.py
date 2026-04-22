"""检查 ApprovalChain 表的当前结构"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def check_table_structure():
    """检查 eims_app_approvalchain 表的结构"""
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE eims_app_approvalchain")
        columns = cursor.fetchall()
        
        print("=" * 80)
        print("eims_app_approvalchain 表结构:")
        print("=" * 80)
        print(f"{'字段名':<25} {'类型':<20} {'允许NULL':<10} {'键':<10}")
        print("-" * 80)
        
        for col in columns:
            field_name = col[0]
            field_type = col[1]
            is_null = col[2]
            key = col[3] if len(col) > 3 else ''
            
            # 特别标记角色相关字段
            marker = " ← 角色字段" if 'role' in field_name.lower() else ""
            print(f"{field_name:<25} {field_type:<20} {is_null:<10} {key:<10}{marker}")
        
        print("=" * 80)
        
        # 检查是否有 level_X_role_id 字段
        role_fields = [col[0] for col in columns if 'level' in col[0].lower() and 'role' in col[0].lower()]
        print(f"\n找到的角色字段: {role_fields}")
        
        if 'level_1_role_id' in role_fields:
            print("✓ 数据库列名正确 (使用 _id 后缀)")
        elif 'level_1_role' in role_fields:
            print("⚠ 数据库列名可能需要更新 (缺少 _id 后缀)")
        else:
            print("? 未找到预期的角色字段")

if __name__ == '__main__':
    check_table_structure()
