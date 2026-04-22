from django.db import models
from .base import BaseModel


class Contract(BaseModel):
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('signed', '已签署'),
        ('executing', '执行中'),
        ('completed', '已完成'),
        ('terminated', '已终止'),
        ('cancelled', '已取消'),
    ]
    
    CONTRACT_TYPE_CHOICES = [
        ('engineering', '工程合同'),
        ('service', '服务合同'),
        ('purchase', '采购合同'),
        ('other', '其他合同'),
    ]
    
    status = models.CharField(verbose_name='合同状态', db_index=True, max_length=20, choices=STATUS_CHOICES, default='draft')
    contract_type = models.CharField(verbose_name='合同类型', db_index=True, max_length=20, choices=CONTRACT_TYPE_CHOICES, default='engineering')
    contract_name = models.CharField(verbose_name='合同名称', db_index=True, max_length=255, default='', blank=True)
    contract_code = models.CharField(verbose_name='合同编号', db_index=True, max_length=50, unique=True, null=True, blank=True)
    contract_amount = models.DecimalField(verbose_name='合同金额 (元)', max_digits=12, decimal_places=2, default=0.00)
    signing_time = models.DateField(verbose_name='签订时间', db_index=True, null=True, blank=True)
    project_code = models.CharField(verbose_name='项目编号', max_length=50, blank=True, db_index=True)
    party_a = models.CharField(verbose_name='甲方', max_length=200, blank=True)
    project_name = models.CharField(verbose_name='项目名称', max_length=255, blank=True)
    project_address = models.CharField(verbose_name='项目地址', max_length=255, blank=True)
    project_scale = models.CharField(verbose_name='项目规模', max_length=100, blank=True)
    project_investment = models.DecimalField(verbose_name='项目投资(万元)', max_digits=15, decimal_places=2, default=0)
    contract_party_a = models.CharField(verbose_name='甲方', max_length=200, blank=True)
    contract_party_b = models.CharField(verbose_name='乙方', max_length=200, blank=True)
    contract_text = models.TextField(verbose_name='合同文本', blank=True)
    payment_agreement = models.TextField(verbose_name='付款协议', blank=True)
    agreed_staffing = models.CharField(verbose_name='约定人员', max_length=200, blank=True)
    service_period = models.CharField(verbose_name='服务期限', max_length=100, blank=True)
    service_deadline = models.DateField(verbose_name='服务截止日期', null=True, blank=True)
    planned_start_time = models.DateField(verbose_name='计划开始时间', null=True, blank=True)
    estimated_completion_time = models.DateField(verbose_name='预计完成时间', null=True, blank=True)
    extension_agreement = models.CharField(verbose_name='延期协议', max_length=200, blank=True)
    remark = models.TextField(verbose_name='备注', blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-signing_time']),
            models.Index(fields=['contract_type', '-signing_time']),
        ]
        verbose_name = '合同信息'
        verbose_name_plural = '合同信息'
        db_table = 'eims_app_Contract'

    def __str__(self):
        return self.contract_name or f"合同{self.id}"
