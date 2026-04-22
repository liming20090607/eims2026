"""
租户模块权限模型 - 用于配置不同公司可用的业务模块
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantModule(models.Model):
    """系统业务模块定义"""
    
    MODULE_CHOICES = [
        ('preparation', '前期准备'),
        ('bidding', '招标投标'),
        ('design', '工程设计'),
        ('cost', '造价咨询'),
        ('supervision', '工程监理'),
        ('construction', '工程施工'),
        ('testing', '工程检测'),
    ]
    
    code = models.CharField("模块代码", max_length=50, unique=True, 
                           help_text="模块的唯一标识代码")
    name = models.CharField("模块名称", max_length=100)
    icon = models.CharField("图标", max_length=50, default='bi-folder',
                           help_text="Bootstrap Icons 类名，如：bi-clipboard-data")
    description = models.TextField("描述", blank=True)
    sort_order = models.IntegerField("排序", default=0,
                                    help_text="数字越小越靠前")
    is_active = models.BooleanField("是否启用", default=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = '业务模块'
        verbose_name_plural = '业务模块管理'
        ordering = ['sort_order', 'code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class TenantModulePermission(models.Model):
    """租户模块权限 - 记录每个公司启用的业务模块"""
    
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='module_permissions',
        verbose_name="租户公司"
    )
    module = models.ForeignKey(
        TenantModule,
        on_delete=models.CASCADE,
        related_name='tenant_permissions',
        verbose_name="业务模块"
    )
    is_enabled = models.BooleanField("是否启用", default=True,
                                     help_text="勾选表示该公司可以使用此模块")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = '租户模块权限'
        verbose_name_plural = '租户模块权限管理'
        unique_together = ['tenant', 'module']
        ordering = ['tenant', 'module__sort_order']
        indexes = [
            models.Index(fields=['tenant', 'is_enabled']),
            models.Index(fields=['module', 'is_enabled']),
        ]
    
    def __str__(self):
        status = "✓ 启用" if self.is_enabled else "✗ 禁用"
        return f"{self.tenant.short_name} - {self.module.name} ({status})"
