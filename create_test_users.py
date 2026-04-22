"""
创建测试用户以验证登录路由逻辑
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserProfile, UserTenantRelation

def create_test_users():
    """创建测试用户"""
    
    print("="*80)
    print("创建测试用户")
    print("="*80)
    
    # 获取租户
    dingce = Tenant.objects.get(code='dingce')
    shengchang = Tenant.objects.get(code='shengchang')
    jiachengda = Tenant.objects.get(code='jiachengda')
    
    test_cases = [
        {
            'username': 'test_single_dingce',
            'password': 'Test@123456',
            'name': '单公司测试-鼎策',
            'tenants': [dingce],
            'description': '只属于鼎策，应自动跳转到 /dingce/'
        },
        {
            'username': 'test_multi_company',
            'password': 'Test@123456',
            'name': '多公司测试',
            'tenants': [dingce, shengchang],
            'description': '属于鼎策和晟昌，应显示公司选择界面'
        },
        {
            'username': 'test_no_company',
            'password': 'Test@123456',
            'name': '无公司测试',
            'tenants': [],
            'description': '不属于任何公司，应显示错误提示'
        },
    ]
    
    for case in test_cases:
        print(f"\n创建测试用户: {case['username']}")
        print(f"  姓名: {case['name']}")
        print(f"  描述: {case['description']}")
        
        # 创建或获取用户
        user, created = User.objects.get_or_create(
            username=case['username'],
            defaults={
                'first_name': case['name'],
                'email': f"{case['username']}@test.com",
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        if created:
            user.set_password(case['password'])
            user.save()
            print(f"  ✓ 用户已创建")
        else:
            print(f"  ⊘ 用户已存在")
        
        # 创建UserProfile
        profile, profile_created = UserProfile.objects.get_or_create(user=user)
        if profile_created:
            print(f"  ✓ UserProfile已创建")
        
        # 清除旧的租户关系
        UserTenantRelation.objects.filter(user=user).delete()
        
        # 添加新的租户关系
        for tenant in case['tenants']:
            relation, rel_created = UserTenantRelation.objects.get_or_create(
                user=user,
                tenant=tenant
            )
            if rel_created:
                print(f"  ✓ 已关联租户: {tenant.name}")
        
        # 如果是单公司，设置为主租户
        if len(case['tenants']) == 1:
            profile.tenant = case['tenants'][0]
            profile.save(update_fields=['tenant'])
            print(f"  ✓ 主租户设置为: {case['tenants'][0].name}")
    
    print("\n" + "="*80)
    print("测试用户创建完成!")
    print("="*80)
    print("\n测试账号:")
    print("-" * 80)
    print(f"{'用户名':<25} {'密码':<15} {'预期行为'}")
    print("-" * 80)
    print(f"{'test_single_dingce':<25} {'Test@123456':<15} {'自动跳转到 /dingce/'}")
    print(f"{'test_multi_company':<25} {'Test@123456':<15} {'显示公司选择界面'}")
    print(f"{'test_no_company':<25} {'Test@123456':<15} {'显示错误提示'}")
    print(f"{'admin (超级管理员)':<25} {'Admin@123456':<15} {'跳转到 /root/'}")
    print("-" * 80)
    
    print("\n测试步骤:")
    print("1. 访问 http://127.0.0.1:8000/login/")
    print("2. 使用上述测试账号登录")
    print("3. 观察跳转行为是否符合预期")
    print("="*80)

if __name__ == '__main__':
    create_test_users()
