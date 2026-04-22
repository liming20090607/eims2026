"""
一次性数据同步脚本

功能：将现有员工数据与用户账号进行同步
运行方式：python manage.py shell < scripts/sync_all_data.py

使用方法：
1. 命令行运行：python manage.py shell
2. 导入执行：exec(open('scripts/sync_all_data.py').read())
3. 或直接运行：python scripts/sync_all_data.py
"""

import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Employee, UserProfile, UserTenantRelation, Tenant

User = get_user_model()

def sync_all():
    """同步所有现有员工数据到用户系统"""
    print("=" * 60)
    print("🔄 开始同步员工数据到用户系统")
    print("=" * 60)
    
    employees = Employee.objects.filter(is_deleted=False)
    total = employees.count()
    created = 0
    updated = 0
    skipped = 0
    errors = 0
    
    print(f"\n📊 找到 {total} 个未删除的员工记录\n")
    
    for idx, emp in enumerate(employees, 1):
        try:
            # 确定用户名
            username = None
            if emp.mobile:
                username = emp.mobile
            elif emp.employee_code:
                username = emp.employee_code
            
            if not username:
                print(f"  ⚠️  [{idx}/{total}] {emp.name} - 缺少手机号和员工编号，跳过")
                skipped += 1
                continue
            
            # 查找用户
            user = User.objects.filter(username=username).first()
            
            if not user:
                # 创建新用户
                default_password = 'sc123456#'
                user = User.objects.create_user(
                    username=username,
                    password=default_password,
                    first_name=emp.name,
                )
                created += 1
                
                # 创建 UserProfile
                profile = UserProfile.objects.create(
                    user=user,
                    real_name=emp.name,
                    phone=emp.mobile or '',
                    tenant=emp.tenant,
                )
                
                # 创建用户-公司关联
                if emp.tenant:
                    UserTenantRelation.objects.create(
                        user=user,
                        tenant=emp.tenant,
                        is_primary=True,
                        remark='批量同步创建'
                    )
                
                print(f"  ✅ [{idx}/{total}] {emp.name} ({username}) - 已创建用户")
            else:
                # 更新现有用户
                updated_profile = False
                
                # 更新 UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if not profile.real_name:
                    profile.real_name = emp.name
                    updated_profile = True
                if emp.mobile and not profile.phone:
                    profile.phone = emp.mobile
                    updated_profile = True
                if emp.tenant and not profile.tenant:
                    profile.tenant = emp.tenant
                    updated_profile = True
                
                if updated_profile:
                    profile.save()
                
                # 创建用户-公司关联（如果不存在）
                if emp.tenant:
                    relation, created_rel = UserTenantRelation.objects.get_or_create(
                        user=user,
                        tenant=emp.tenant,
                        defaults={'is_primary': True, 'remark': '批量同步创建'}
                    )
                
                updated += 1
                print(f"  🔵 [{idx}/{total}] {emp.name} ({username}) - 已同步")
        
        except Exception as e:
            errors += 1
            print(f"  ❌ [{idx}/{total}] {emp.name} - 错误: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 同步完成统计")
    print("=" * 60)
    print(f"  ✅ 新建用户: {created}")
    print(f"  🔵 更新用户: {updated}")
    print(f"  ⚠️  跳过: {skipped}")
    print(f"  ❌ 错误: {errors}")
    print("=" * 60)
    print("\n💡 提示：")
    print("  - 新建用户的默认密码为: sc123456#")
    print("  - 所有用户已自动关联到对应的公司")
    print("  - 以后新增/修改员工信息时，系统将自动同步到用户账号")
    print("=" * 60)


if __name__ == '__main__':
    sync_all()
