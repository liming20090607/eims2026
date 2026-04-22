"""
造价咨询模块 - 提醒通知模型
"""
from django.db import models
from django.conf import settings


class CostConsultingReminder(models.Model):
    """造价咨询业务提醒表"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               db_index=True,
                               db_constraint=False)
    
    # ===== 关联信息 =====
    project = models.ForeignKey(
        'CostProjectUnified',
        on_delete=models.CASCADE,
        related_name='cost_reminders',
        verbose_name="关联项目",
        null=True,
        blank=True,
        db_constraint=False
    )
    
    # ===== 人员信息 =====
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="发送人",
        related_name="sent_cost_reminders",
        db_constraint=False
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="接收人",
        related_name="received_cost_reminders",
        db_constraint=False
    )
    
    # ===== 提醒内容 =====
    REMINDER_TYPE_CHOICES = [
        ('new_project', '新项目待分配'),
        ('task_assigned', '任务已分配'),
        ('compilation_start', '开始编制'),
        ('review_start', '开始审核'),
        ('archive_submit', '归档申请提交'),
        ('archive_approve', '归档审批待处理'),
        ('archive_receive', '档案待接收'),
        ('other', '其他'),
    ]
    reminder_type = models.CharField("提醒类型", max_length=30, choices=REMINDER_TYPE_CHOICES, default='other')
    title = models.CharField("提醒标题", max_length=200)
    content = models.TextField("提醒内容")
    link_url = models.URLField("跳转链接", blank=True, help_text="点击提醒后跳转的页面地址")
    
    # ===== 状态管理 =====
    STATUS_CHOICES = [
        ('unread', '未读'),
        ('read', '已读'),
        ('ignored', '已忽略'),
    ]
    status = models.CharField("阅读状态", max_length=10, choices=STATUS_CHOICES, default='unread', db_index=True)
    
    # ===== 忽略与延迟 =====
    snooze_until = models.DateTimeField("延迟提醒时间", null=True, blank=True, help_text="延迟到该时间再次提醒")
    ignored_session = models.CharField("忽略会话ID", max_length=100, blank=True, help_text="本次登录期间忽略的提醒会话ID")
    
    # ===== 系统字段 =====
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    read_at = models.DateTimeField("阅读时间", null=True, blank=True)
    
    class Meta:
        verbose_name = "造价咨询提醒"
        verbose_name_plural = "造价咨询提醒管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['tenant', 'status']),
        ]
    
    def __str__(self):
        return f"[{self.get_reminder_type_display()}] {self.receiver.username} - {self.title}"
