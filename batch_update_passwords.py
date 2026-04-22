"""
批量更新用户密码脚本
- 广西鼎策、广西晟昌公司用户：sc123456#
- 广西嘉诚达公司用户：jcd123456#
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, 'E:\\EIMS2026')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# 应用Python 3.14兼容性补丁
import python314_patch

django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserTenantRelation

User = get_user_model()

def update_user_passwords():
    """批量更新用户密码"""
    
    print("=" * 100)
    print("批量更新用户密码")
    print("=" * 100)
    
    # 获取租户
    try:
        tenant_dingce = Tenant.objects.get(code='dingce')
        tenant_shengchang = Tenant.objects.get(code='shengchang')
        tenant_jiachengda = Tenant.objects.get(code='jiachengda')
    except Tenant.DoesNotExist as e:
        print(f"❌ 租户不存在：{e}")
        return
    
    # 定义密码
    password_dingce_shengchang = 'sc123456#'
    password_jiachengda = 'jcd123456#'
    
    print(f"\n📋 密码配置：")
    print(f"  广西鼎策、广西晟昌：{password_dingce_shengchang}")
    print(f"  广西嘉诚达：{password_jiachengda}")
    print()
    
    # 统计信息
    stats = {
        'dingce': {'success': 0, 'failed': 0, 'users': []},
        'shengchang': {'success': 0, 'failed': 0, 'users': []},
        'jiachengda': {'success': 0, 'failed': 0, 'users': []},
    }
    
    # 处理鼎策公司用户
    print("=" * 100)
    print("【1】广西鼎策工程顾问有限责任公司")
    print("=" * 100)
    relations_dingce = UserTenantRelation.objects.filter(tenant=tenant_dingce).select_related('user')
    for rel in relations_dingce:
        user = rel.user
        try:
            user.set_password(password_dingce_shengchang)
            user.save(update_fields=['password'])
            stats['dingce']['success'] += 1
            stats['dingce']['users'].append(user.username)
            print(f"  ✅ {user.username} ({user.first_name or '-'}) - 密码更新成功")
        except Exception as e:
            stats['dingce']['failed'] += 1
            print(f"  ❌ {user.username} - 密码更新失败：{str(e)}")
    
    print(f"\n  📊 鼎策公司统计：成功 {stats['dingce']['success']} 人，失败 {stats['dingce']['failed']} 人\n")
    
    # 处理晟昌公司用户
    print("=" * 100)
    print("【2】广西晟昌工程科技有限责任公司")
    print("=" * 100)
    relations_shengchang = UserTenantRelation.objects.filter(tenant=tenant_shengchang).select_related('user')
    for rel in relations_shengchang:
        user = rel.user
        try:
            user.set_password(password_dingce_shengchang)
            user.save(update_fields=['password'])
            stats['shengchang']['success'] += 1
            stats['shengchang']['users'].append(user.username)
            print(f"  ✅ {user.username} ({user.first_name or '-'}) - 密码更新成功")
        except Exception as e:
            stats['shengchang']['failed'] += 1
            print(f"  ❌ {user.username} - 密码更新失败：{str(e)}")
    
    print(f"\n  📊 晟昌公司统计：成功 {stats['shengchang']['success']} 人，失败 {stats['shengchang']['failed']} 人\n")
    
    # 处理嘉诚达公司用户
    print("=" * 100)
    print("【3】广西嘉诚达工程造价咨询有限公司")
    print("=" * 100)
    relations_jiachengda = UserTenantRelation.objects.filter(tenant=tenant_jiachengda).select_related('user')
    for rel in relations_jiachengda:
        user = rel.user
        try:
            user.set_password(password_jiachengda)
            user.save(update_fields=['password'])
            stats['jiachengda']['success'] += 1
            stats['jiachengda']['users'].append(user.username)
            print(f"  ✅ {user.username} ({user.first_name or '-'}) - 密码更新成功")
        except Exception as e:
            stats['jiachengda']['failed'] += 1
            print(f"  ❌ {user.username} - 密码更新失败：{str(e)}")
    
    print(f"\n  📊 嘉诚达公司统计：成功 {stats['jiachengda']['success']} 人，失败 {stats['jiachengda']['failed']} 人\n")
    
    # 总体统计
    print("=" * 100)
    print("📊 总体统计")
    print("=" * 100)
    total_success = stats['dingce']['success'] + stats['shengchang']['success'] + stats['jiachengda']['success']
    total_failed = stats['dingce']['failed'] + stats['shengchang']['failed'] + stats['jiachengda']['failed']
    
    print(f"  ✅ 广西鼎策：成功 {stats['dingce']['success']} 人，失败 {stats['dingce']['failed']} 人")
    print(f"  ✅ 广西晟昌：成功 {stats['shengchang']['success']} 人，失败 {stats['shengchang']['failed']} 人")
    print(f"  ✅ 广西嘉诚达：成功 {stats['jiachengda']['success']} 人，失败 {stats['jiachengda']['failed']} 人")
    print(f"\n  📈 总计：成功 {total_success} 人，失败 {total_failed} 人")
    print()
    
    # 显示用户名列表
    print("=" * 100)
    print("📝 已更新密码的用户列表")
    print("=" * 100)
    print(f"\n【广西鼎策】({len(stats['dingce']['users'])} 人)")
    for username in stats['dingce']['users']:
        print(f"  • {username}")
    
    print(f"\n【广西晟昌】({len(stats['shengchang']['users'])} 人)")
    for username in stats['shengchang']['users']:
        print(f"  • {username}")
    
    print(f"\n【广西嘉诚达】({len(stats['jiachengda']['users'])} 人)")
    for username in stats['jiachengda']['users']:
        print(f"  • {username}")
    
    print("\n" + "=" * 100)
    print("✅ 密码批量更新完成！")
    print("=" * 100)

if __name__ == '__main__':
    update_user_passwords()
