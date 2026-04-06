@echo off
chcp 65001 >nul
title Force Restore Role Data
echo ========================================
echo   Force Restore Role Data
echo ========================================
echo.

ssh root@39.106.41.239 << 'SSHEOF'
cd /var/www/eims
source venv/bin/activate

echo "=== 开始强制恢复角色数据 ==="

python3 << 'PYEOF'
import sys
import os
sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from eims_app.models import Role
import json

print("\n步骤 1: 读取本地备份的角色数据")
print("=" * 50)

# 直接从 JSON 字符串中恢复（使用之前上传的原始文件）
role_json_str = '''[
{
  "model": "eims_app.role",
  "pk": 1,
  "fields": {
    "name": "super_admin",
    "description": "拥有系统所有权限",
    "permissions": "view,edit,submit"
  }
},
{
  "model": "eims_app.role",
  "pk": 2,
  "fields": {
    "name": "system_admin",
    "description": "拥有系统管理权限",
    "permissions": "view,edit,submit"
  }
},
{
  "model": "eims_app.role",
  "pk": 3,
  "fields": {
    "name": "project_director",
    "description": "负责项目整体管理和最终审核",
    "permissions": "view,edit,submit"
  }
},
{
  "model": "eims_app.role",
  "pk": 4,
  "fields": {
    "name": "director_rep",
    "description": "协助总监工作，可初审",
    "permissions": "view,edit,submit"
  }
},
{
  "model": "eims_app.role",
  "pk": 5,
  "fields": {
    "name": "supervisor",
    "description": "现场监理，发起填报",
    "permissions": "view,edit,submit"
  }
},
{
  "model": "eims_app.role",
  "pk": 6,
  "fields": {
    "name": "data_clerk",
    "description": "负责资料管理，发起填报",
    "permissions": "view,edit,submit"
  }
},
{
  "model": "eims_app.role",
  "pk": 7,
  "fields": {
    "name": "initiator",
    "description": "普通发起人员",
    "permissions": "view,edit,submit"
  }
}
]'''

role_data = json.loads(role_json_str)
print(f"读取到 {len(role_data)} 条角色数据")

print("\n步骤 2: 清除现有角色数据")
print("=" * 50)
Role.objects.all().delete()
print("✓ 已清除所有现有角色数据")

print("\n步骤 3: 逐条创建角色")
print("=" * 50)

success_count = 0
error_count = 0

for obj in role_data:
    try:
        pk = obj['pk']
        fields = obj['fields']
        
        # 创建角色
        role = Role.objects.create(
            id=pk,
            name=fields['name'],
            description=fields['description'],
            permissions=fields['permissions']
        )
        success_count += 1
        print(f"✓ ID={role.id}, Name={role.name}, Description={role.description}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ 错误 (PK={obj.get('pk', '?')}): {e}")

print(f"\n完成！成功：{success_count}, 失败：{error_count}")

print("\n步骤 4: 验证数据库中的角色数据")
print("=" * 50)
all_roles = Role.objects.all().order_by('id')
print(f"数据库中共有 {len(all_roles)} 个角色:")
for role in all_roles:
    print(f"  - ID={role.id}, Name={role.name}, Desc={role.description[:30]}...")

PYEOF

SSHEOF

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Role Data Restored Successfully!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Refresh browser (F5)
    echo   2. Check Role Configuration page
    echo   3. Should see 7 roles
    echo.
) else (
    echo.
    echo ========================================
    echo   Restore Failed!
    echo ========================================
    echo.
    echo Please check error messages above.
)

pause
