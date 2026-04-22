"""
子模块模型 - 支持一级模块下的子模块权限控制
"""
from django.db import models


class SubModule(models.Model):
    """子模块定义 - 隶属于一级业务模块"""
    
    parent_module = models.ForeignKey(
        'TenantModule',
        on_delete=models.CASCADE,
        related_name='submodules',
        verbose_name='所属一级模块'
    )
    code = models.CharField("子模块代码", max_length=50)
    name = models.CharField("子模块名称", max_length=100)
    icon = models.CharField("图标", max_length=50, default='bi-circle',
                          help_text='Bootstrap Icons class，如 bi-file-text')
    url_name = models.CharField("URL名称", max_length=100, blank=True,
                               help_text='Django URL name，如 eims_app:contract_approval_chain')
    url_pattern = models.CharField("URL匹配模式", max_length=200, blank=True,
                                  help_text='用于高亮当前菜单，如 /contract-approval')
    description = models.TextField("描述", blank=True)
    sort_order = models.IntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        db_table = 'eims_sub_module'
        ordering = ['sort_order', 'code']
        unique_together = ['parent_module', 'code']
        verbose_name = '子模块定义'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.parent_module.name} - {self.name}"


class TenantSubModulePermission(models.Model):
    """租户子模块权限 - 控制每个公司可使用的子模块"""
    
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='sub_module_permissions',
        verbose_name='租户公司'
    )
    sub_module = models.ForeignKey(
        SubModule,
        on_delete=models.CASCADE,
        related_name='tenant_permissions',
        verbose_name='子模块'
    )
    is_enabled = models.BooleanField("是否启用", default=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        db_table = 'eims_tenant_sub_module_permission'
        unique_together = ['tenant', 'sub_module']
        verbose_name = '租户子模块权限'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.tenant.name} - {self.sub_module.name} ({'启用' if self.is_enabled else '禁用'})"
