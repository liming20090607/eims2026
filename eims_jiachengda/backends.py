from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class ChineseUsernameAuthenticationBackend(ModelBackend):
    """
    支持多种登录方式的认证后端：
    1. username (可以是中文)
    2. real_name (真实姓名，来自 UserProfile)
    3. email (邮箱)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        支持使用 username、real_name 或 email 登录
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        # 尝试通过 username 或 email 查找用户
        user = self._get_user_by_username_or_email(username)
        
        # 如果没找到，尝试通过 real_name 查找
        if not user:
            user = self._get_user_by_real_name(username)
        
        # 验证密码
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def _get_user_by_username_or_email(self, identifier):
        """
        通过 username 或 email 查找用户
        """
        try:
            # 使用 Q 对象进行 OR 查询
            users = User.objects.filter(
                Q(username=identifier) | Q(email=identifier)
            )
            
            if users.count() == 1:
                return users.first()
            elif users.count() > 1:
                # 如果有多个匹配，优先返回 username 匹配的
                for user in users:
                    if user.username == identifier:
                        return user
                return users.first()
        except User.DoesNotExist:
            pass
        
        return None
    
    def _get_user_by_real_name(self, real_name):
        """
        通过真实姓名查找用户
        """
        try:
            # 在 UserProfile 中查找 real_name
            from eims_app.models.model_user import UserProfile
            
            profiles = UserProfile.objects.filter(real_name=real_name)
            
            if profiles.count() == 1:
                return profiles.first().user
            elif profiles.count() > 1:
                # 如果有多个同名用户，返回第一个有效的
                for profile in profiles:
                    if profile.user.is_active:
                        return profile.user
        except Exception:
            pass
        
        return None
    
    def get_user(self, user_id):
        """
        根据用户 ID 获取用户
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
