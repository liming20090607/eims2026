from django.db import models


class Tenant(models.Model):
    """租户（公司）模型 - 用于多租户数据隔离"""
    
    code = models.CharField("公司代码", max_length=50, unique=True, 
                           help_text="公司的唯一标识代码，如：COMPANY_A")
    name = models.CharField("公司名称", max_length=200)
    short_name = models.CharField("简称", max_length=50)
    logo = models.ImageField("Logo", upload_to='tenants/logos/', blank=True, null=True,
                            help_text="公司Logo图片")
    contact_person = models.CharField("联系人", max_length=100, blank=True)
    contact_phone = models.CharField("联系电话", max_length=20, blank=True)
    contact_email = models.EmailField("联系邮箱", blank=True)
    address = models.TextField("公司地址", blank=True)
    project_code_prefix = models.CharField("项目编号前缀", max_length=10, blank=True, default='',
                                           help_text="新建项目编号的默认前缀，如：JCD、DC、SC")
    is_active = models.BooleanField("是否启用", default=True)
    remark = models.TextField("备注", blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = '租户公司'
        verbose_name_plural = '租户公司管理'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_active_user_count(self):
        """获取该公司的活跃用户数量"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(profile__tenant=self, is_active=True).count()
    
    def get_project_count(self):
        """获取该公司的项目数量"""
        from eims_app.models import ProjectDetail
        return ProjectDetail.objects.filter(tenant=self).count()
