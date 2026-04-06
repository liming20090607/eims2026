# 检查用户手机号绑定情况
from eims_app.models.model_user import UserProfile

profiles = UserProfile.objects.all()
print(f'总用户资料数: {profiles.count()}')
print('\n手机号绑定情况:')
for p in profiles:
    phone_status = '已绑定: ' + p.phone if p.phone else '未绑定'
    real_name = p.real_name or '未设置'
    print(f'  {p.user.username} - {real_name}: {phone_status}')
