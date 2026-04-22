from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from eims_app.models.model_user import UserProfile

UserModel = get_user_model()

class UsernameOrNameAuthBackend(ModelBackend):
    """
    自定义认证后端，支持使用拼音用户名或中文姓名登录
    
    用户可以使用以下任一方式登录：
    - 拼音用户名（如：zhangsan）
    - 中文姓名/真实姓名（如：张三）
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 获取用户名参数
        login_username = username
        
        if login_username is None:
            return None
            
        # 尝试使用 username 字段匹配（拼音用户名）
        try:
            user = UserModel.objects.get(username=login_username)
        except UserModel.DoesNotExist:
            # 如果没有找到，尝试使用 UserProfile 的 real_name 字段匹配（中文姓名）
            try:
                profile = UserProfile.objects.select_related('user').get(real_name=login_username)
                user = profile.user
            except UserProfile.DoesNotExist:
                # 都没找到，返回 None
                # 运行默认密码哈希器以进行恒定时间比较，防止时序攻击
                try:
                    UserModel().set_password(password)
                except AttributeError:
                    pass
                return None
        
        # 验证密码
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        user = UserModel.objects.get(pk=user_id)
        if user and self.user_can_authenticate(user):
            return user
        return None
