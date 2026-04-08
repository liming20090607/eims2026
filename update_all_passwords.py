"""
批量更新用户密码脚本
将所有密码为 'Abc123456!' 的用户密码更新为 'sc123456#'
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def update_passwords():
    """批量更新密码"""
    old_password = 'Abc123456!'
    new_password = 'sc123456#'
    
    # 获取所有用户
    all_users = User.objects.all()
    updated_count = 0
    skipped_count = 0
    
    print(f"开始检查用户密码...")
    print(f"旧密码: {old_password}")
    print(f"新密码: {new_password}")
    print("=" * 50)
    
    for user in all_users:
        # 检查用户密码是否匹配旧密码
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            updated_count += 1
            print(f"✓ 已更新: {user.username} ({user.get_full_name() or '未设置姓名'})")
        else:
            skipped_count += 1
            print(f"- 跳过: {user.username} (密码不匹配或是管理员)")
    
    print("=" * 50)
    print(f"更新完成！")
    print(f"总共检查: {all_users.count()} 个用户")
    print(f"成功更新: {updated_count} 个用户")
    print(f"跳过: {skipped_count} 个用户")

if __name__ == '__main__':
    update_passwords()
