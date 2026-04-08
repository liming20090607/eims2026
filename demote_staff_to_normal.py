"""
将普通管理员降级为一般用户
"""
import os
import sys
import django

sys.path.append(r'e:\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 要降级的用户列表
usernames = [
    '秦方玉', '王璐', '汪勇', '唐昌成', '唐昌罗', 
    '秦养付', '王立明', '李闰', 'gxsc', '王敏志', 
    '易强', '唐满东', '秦林', '银雪', '唐薇薇', 
    '方永明', '宋弦弦', '秦隆刚', '黄建波', '廖志红', '程慧慧'
]

print("=" * 60)
print("将普通管理员降级为一般用户")
print("=" * 60)

success_count = 0
fail_count = 0
not_found_count = 0

for username in usernames:
    try:
        user = User.objects.get(username=username)
        
        # 检查当前状态
        old_is_staff = user.is_staff
        old_is_superuser = user.is_superuser
        
        # 降级为一般用户
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        success_count += 1
        print(f"✓ {username:10s} - 已降级 (is_staff: {old_is_staff}→False, is_superuser: {old_is_superuser}→False)")
        
    except User.DoesNotExist:
        not_found_count += 1
        print(f"✗ {username:10s} - 用户不存在")
    except Exception as e:
        fail_count += 1
        print(f"✗ {username:10s} - 降级失败: {str(e)}")

print("\n" + "=" * 60)
print(f"处理完成！")
print(f"成功降级: {success_count} 个用户")
print(f"用户不存在: {not_found_count} 个")
print(f"降级失败: {fail_count} 个")
print("=" * 60)

# 验证结果
print("\n验证降级结果：")
print("-" * 60)
for username in usernames:
    try:
        user = User.objects.get(username=username)
        if not user.is_staff and not user.is_superuser:
            print(f"✓ {username:10s} - 已确认降级为一般用户")
        else:
            print(f"✗ {username:10s} - 降级失败 (is_staff={user.is_staff}, is_superuser={user.is_superuser})")
    except User.DoesNotExist:
        pass
