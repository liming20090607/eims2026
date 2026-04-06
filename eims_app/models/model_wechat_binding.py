from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class WechatUserBinding(models.Model):
    """微信用户绑定关系"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wechat_bindings',
        verbose_name='系统用户'
    )
    
    # 微信唯一标识
    openid = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name='微信OpenID'
    )
    
    unionid = models.CharField(
        max_length=100,
        blank=True,
        default='',
        db_index=True,
        verbose_name='微信UnionID'
    )
    
    # 微信用户信息
    nickname = models.CharField(max_length=100, blank=True, verbose_name='微信昵称')
    headimgurl = models.URLField(blank=True, verbose_name='微信头像')
    sex = models.SmallIntegerField(default=0, verbose_name='性别')
    country = models.CharField(max_length=50, blank=True, verbose_name='国家')
    province = models.CharField(max_length=50, blank=True, verbose_name='省份')
    city = models.CharField(max_length=50, blank=True, verbose_name='城市')
    
    # 绑定状态
    is_bound = models.BooleanField(default=True, verbose_name='是否已绑定')
    bind_time = models.DateTimeField(auto_now_add=True, verbose_name='绑定时间')
    last_login_time = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    
    # 额外信息
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='额外数据')
    
    class Meta:
        verbose_name = '微信用户绑定'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['openid']),
            models.Index(fields=['unionid']),
            models.Index(fields=['user', 'is_bound']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.nickname or self.openid[:8]}"
    
    @staticmethod
    def get_user_by_openid(openid):
        """通过openid获取绑定的用户"""
        try:
            binding = WechatUserBinding.objects.get(openid=openid, is_bound=True)
            return binding.user
        except WechatUserBinding.DoesNotExist:
            return None
    
    @staticmethod
    def bind_user(user, openid, unionid='', **kwargs):
        """绑定微信用户"""
        binding, created = WechatUserBinding.objects.update_or_create(
            openid=openid,
            defaults={
                'user': user,
                'unionid': unionid,
                'is_bound': True,
                'last_login_time': timezone.now(),
                **kwargs
            }
        )
        return binding, created


class WechatQRCodeSession(models.Model):
    """微信扫码登录会话（用于网站应用扫码）"""
    
    STATUS_CHOICES = [
        ('pending', '等待扫码'),
        ('scanned', '已扫码'),
        ('authorized', '已授权'),
        ('bound', '已绑定'),
        ('cancelled', '已取消'),
        ('expired', '已过期'),
    ]
    
    # 唯一标识
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='会话ID'
    )
    
    # 微信返回的state参数（用于防止CSRF）
    state = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name='State参数'
    )
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    
    # 微信返回的信息
    code = models.CharField(max_length=200, blank=True, verbose_name='授权码')
    openid = models.CharField(max_length=100, blank=True, verbose_name='OpenID')
    unionid = models.CharField(max_length=100, blank=True, verbose_name='UnionID')
    
    # 绑定的用户
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='用户'
    )
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    scanned_at = models.DateTimeField(null=True, blank=True, verbose_name='扫码时间')
    authorized_at = models.DateTimeField(null=True, blank=True, verbose_name='授权时间')
    
    # IP地址
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    
    class Meta:
        verbose_name = '微信扫码登录会话'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f'Wechat QR: {str(self.session_id)[:8]}... ({self.get_status_display()})'
    
    def is_expired(self):
        """检查是否过期"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """检查是否有效"""
        return not self.is_expired() and self.status in ['pending', 'scanned']
    
    @staticmethod
    def create_session(ip_address=None):
        """创建新的扫码会话"""
        import secrets
        expires_at = timezone.now() + timedelta(minutes=10)
        state = secrets.token_urlsafe(32)  # 生成随机state
        
        session = WechatQRCodeSession.objects.create(
            state=state,
            status='pending',
            expires_at=expires_at,
            ip_address=ip_address
        )
        return session
