from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class WechatQRLogin(models.Model):
    """微信扫码登录记录"""
    
    STATUS_CHOICES = [
        ('pending', '等待扫码'),
        ('scanned', '已扫码'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
        ('expired', '已过期'),
    ]
    
    # 唯一二维码标识
    qr_code = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name='二维码标识'
    )
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    
    # 关联的用户（扫码确认后填写）
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='用户'
    )
    
    # 扫码时间
    scanned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='扫码时间'
    )
    
    # 确认时间
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='确认时间'
    )
    
    # 过期时间（10分钟后过期）
    expires_at = models.DateTimeField(
        verbose_name='过期时间'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    # IP地址
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP地址'
    )
    
    # 额外信息（JSON格式）
    extra_data = models.TextField(
        blank=True,
        default='{}',
        verbose_name='额外信息'
    )
    
    class Meta:
        verbose_name = '微信二维码登录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['qr_code']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"QR: {str(self.qr_code)[:8]}... - {self.get_status_display()}"
    
    def is_expired(self):
        """检查是否过期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def get_extra_data_dict(self):
        """获取额外数据的字典格式"""
        try:
            return json.loads(self.extra_data) if self.extra_data else {}
        except:
            return {}
    
    def set_extra_data(self, data_dict):
        """设置额外数据"""
        self.extra_data = json.dumps(data_dict)
