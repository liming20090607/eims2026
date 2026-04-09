import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

# 检查是否已有公司
if Tenant.objects.exists():
    print("Tenant 表已有数据，跳过初始化")
    for t in Tenant.objects.all():
        print(f"  - {t.name} (code: {t.code}, active: {t.is_active})")
else:
    print("正在创建默认公司...")
    
    # 创建默认公司
    tenant = Tenant.objects.create(
        name='协同AI办公系统',
        code='XTCOAI',
        is_active=True,
        remark='默认公司'
    )
    print(f"✓ 已创建公司: {tenant.name} (code: {tenant.code})")
    
    # 将超级管理员关联到此公司
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            # 更新 UserProfile 的 tenant 字段
            profile = admin_user.profile
            profile.tenant = tenant
            profile.save()
            print(f"✓ 已将超级管理员 {admin_user.username} 关联到公司: {tenant.name}")
        else:
            print("⚠ 未找到超级管理员用户")
    except Exception as e:
        print(f"⚠ 关联管理员到公司时出错: {e}")

print("\n✅ Tenant 初始化完成！")
