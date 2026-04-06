from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class QRCodeLoginSession(models.Model):
    """二维码登录会话"""
    
    STATUS_CHOICES = [
        ('pending', '等待扫码'),
        ('scanned', '已扫码'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
        ('expired', '已过期'),
    ]
    
    # 二维码唯一标识
    session_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name='会话ID'
    )
    
    # 会话状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    
    # 扫码后选择的用户
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='用户'
    )
    
    # 扫码时间
    scanned_at = models.DateTimeField(null=True, blank=True, verbose_name='扫码时间')
    
    # 确认时间
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    
    # 过期时间
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 客户端IP
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    
    # 额外数据
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='额外数据')
    
    class Meta:
        verbose_name = '二维码登录会话'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f'QR Session: {str(self.session_id)[:8]}... ({self.get_status_display()})'
    
    def is_expired(self):
        """检查是否过期"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """检查是否有效（未过期且状态为pending）"""
        return not self.is_expired() and self.status == 'pending'
    
    @staticmethod
    def create_session(ip_address=None):
        """创建新的登录会话"""
        expires_at = timezone.now() + timedelta(minutes=10)  # 10分钟有效期
        session = QRCodeLoginSession.objects.create(
            status='pending',
            expires_at=expires_at,
            ip_address=ip_address
        )
        return session
    
    @staticmethod
    def get_session(session_id):
        """获取会话"""
        try:
            return QRCodeLoginSession.objects.get(session_id=session_id)
        except QRCodeLoginSession.DoesNotExist:
            return None
