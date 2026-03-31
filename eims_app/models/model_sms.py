from django.db import models
from .base import BaseModel
from django.contrib.auth.models import User


class SMSVerificationRecord(BaseModel):
    """短信验证码记录 - 用于审计和日志"""
    
    VERIFICATION_TYPE_CHOICES = [
        ('login', '登录验证'),
        ('reset_password', '重置密码'),
        ('change_phone', '修改手机号'),
        ('register', '注册验证'),
    ]
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('expired', '过期'),
    ]
    
    # 验证信息
    phone = models.CharField(max_length=20, verbose_name='手机号码', db_index=True)
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPE_CHOICES, verbose_name='验证类型')
    verification_code = models.CharField(max_length=10, verbose_name='验证码')  # 加密存储
    
    # 验证结果
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success', verbose_name='验证状态')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联用户')
    
    # 请求信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP 地址')
    user_agent = models.CharField(max_length=255, blank=True, verbose_name='User-Agent')
    
    # 时间信息
    expire_time = models.DateTimeField(verbose_name='过期时间')
    verified_time = models.DateTimeField(null=True, blank=True, verbose_name='验证时间')
    
    # 备注
    remark = models.TextField(blank=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '短信验证记录'
        verbose_name_plural = '短信验证记录管理'
        ordering = ('-create_time',)
    
    def __str__(self):
        return f'{self.phone} - {self.get_verification_type_display()} - {self.status}'
    
    def is_expired(self):
        """检查验证码是否已过期"""
        from django.utils import timezone
        return timezone.now() > self.expire_time
