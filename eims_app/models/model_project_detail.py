from django.db import models
from django.utils import timezone
import os


class ProjectDetail(models.Model):
    """监理项目信息总表 - 完整的项目合同信息"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True)
    
    # ===== 合同类别 =====
    CONTRACT_CATEGORY_CHOICES = [
        ('engineering_supervision', '工程监理'),
        ('cost_consulting', '造价咨询'),
        ('testing', '检测'),
        ('whole_process_consulting', '全过程咨询'),
    ]
    contract_category = models.CharField("合同类别", max_length=30, choices=CONTRACT_CATEGORY_CHOICES, default='engineering_supervision')
    
    # ===== 基础信息 =====
    monthly_report_required = models.BooleanField("项目月报", default=True, help_text="是否需要提交月报")
    project_code = models.CharField("项目编号", max_length=50, unique=True, db_index=True)
    contract_code = models.CharField("合同编号", max_length=50, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    # 项目状态
    PROJECT_STATUS_CHOICES = [
        ('not_started', '未开工'),
        ('under_construction', '在施工'),
        ('stopped', '在停工'),
        ('completed', '已完工'),
    ]
    project_status = models.CharField("项目状态", max_length=20, choices=PROJECT_STATUS_CHOICES, default='not_started')
    
    # 合同状态
    CONTRACT_STATUS_CHOICES = [
        ('pending_review', '待审核'),
        ('executing', '在执行'),
        ('terminated', '已终止'),
        ('released', '已解除'),
    ]
    contract_status = models.CharField("合同状态", max_length=20, choices=CONTRACT_STATUS_CHOICES, default='pending_review')
    
    # 结算情况
    SETTLEMENT_STATUS_CHOICES = [
        ('unsettled', '未结算'),
        ('settled', '已结算'),
    ]
    settlement_status = models.CharField("结算情况", max_length=20, choices=SETTLEMENT_STATUS_CHOICES, default='unsettled')
    
    # ===== 合同双方 =====
    contract_party_a = models.CharField("合同甲方", max_length=200)
    contract_party_b = models.CharField("合同乙方", max_length=200)
    
    # ===== 合同签订 =====
    signing_date = models.DateField("签订日期", null=True, blank=True)
    
    # 合同文本上传
    def contract_text_upload_path(instance, filename):
        """合同文本上传路径"""
        ext = os.path.splitext(filename)[1]
        return f'contract_texts/{instance.project_code}/{filename}'
    
    contract_text = models.FileField("合同文本", upload_to=contract_text_upload_path, blank=True)
    
    contract_amount = models.DecimalField("合同总价 (元)", max_digits=15, decimal_places=2)
    payment_agreement = models.TextField("付款约定", blank=True)
    
    # ===== 回款信息 =====
    cumulative_payment = models.DecimalField("累计回款 (元)", max_digits=15, decimal_places=2, default=0)
    contract_balance = models.DecimalField("合同余额 (元)", max_digits=15, decimal_places=2, default=0)
    
    # ===== 项目属性 =====
    project_scale = models.CharField("项目规模", max_length=200, blank=True, 
                                   help_text="如：建筑面积 5 万㎡/道路长度 10km")
    project_investment = models.DecimalField("项目总投资 (万元)", max_digits=15, decimal_places=2, 
                                           null=True, blank=True)
    project_address = models.CharField("项目地址", max_length=255, blank=True)
    agreed_staffing = models.CharField("约定人员配备", max_length=200, blank=True)
    service_start_date = models.DateField("服务开始日期", null=True, blank=True)
    service_period_months = models.IntegerField("服务周期 (月)", default=0, help_text="以月为单位")
    service_deadline = models.DateField("服务到期日期", null=True, blank=True)
    
    # ===== 延期管理 =====
    extension_agreement = models.CharField("延期约定", max_length=200, blank=True)
    actual_extension_status = models.CharField("实际延期情况", max_length=200, blank=True)
    
    # ===== 建设手续 =====
    CONSTRUCTION_PERMIT_CHOICES = [
        ('not_started', '未办理'),
        ('in_progress', '办理中'),
        ('completed', '已办理'),
    ]
    construction_permit_status = models.CharField("报建情况", max_length=20, 
                                                   choices=CONSTRUCTION_PERMIT_CHOICES, 
                                                   blank=True, default='')
    
    # 施工许可证上传
    def construction_permit_upload_path(instance, filename):
        """施工许可证上传路径"""
        ext = os.path.splitext(filename)[1]
        return f'construction_permits/{instance.project_code}/{filename}'
    
    construction_permit = models.FileField("施工许可证", upload_to=construction_permit_upload_path, blank=True)
    
    # ===== 进度管理 =====
    ENTRY_NOTICE_CHOICES = [
        ('yes', '有'),
        ('no', '无'),
    ]
    entry_notice = models.CharField("进场通知", max_length=10, choices=ENTRY_NOTICE_CHOICES, default='no')
    
    # 进场通知书上传
    def entry_notice_upload_path(instance, filename):
        """进场通知书上传路径"""
        ext = os.path.splitext(filename)[1]
        return f'entry_notices/{instance.project_code}/{filename}'
    
    entry_notice_document = models.FileField("进场通知书", upload_to=entry_notice_upload_path, blank=True)
    
    entry_time = models.DateField("进场时间", null=True, blank=True)
    planned_start_date = models.DateField("计划开工日期", null=True, blank=True)
    actual_start_date = models.DateField("实际开工日期", null=True, blank=True)
    estimated_completion_date = models.DateField("预计竣工日期", null=True, blank=True)
    
    # ===== 人员信息 =====
    project_director = models.CharField("项目总监", max_length=50, blank=True, db_index=True)
    project_manager = models.CharField("现场负责人", max_length=50, blank=True, db_index=True)
    contact_phone = models.CharField("联系电话", max_length=20, blank=True)
    
    # ===== 辅助信息 =====
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        verbose_name = "监理项目信息"
        verbose_name_plural = "监理项目信息管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
            models.Index(fields=['contract_code']),
            models.Index(fields=['project_status', 'contract_status']),
            models.Index(fields=['contract_category']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    def calculate_service_deadline(self):
        """根据服务开始时间和服务周期计算服务到期时间"""
        if self.service_start_date and self.service_period_months:
            from dateutil.relativedelta import relativedelta
            return self.service_start_date + relativedelta(months=self.service_period_months)
        return None
    
    def save(self, *args, **kwargs):
        """保存时自动计算服务到期时间"""
        if self.service_start_date and self.service_period_months:
            self.service_deadline = self.calculate_service_deadline()
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """检查是否服务到期"""
        if self.service_deadline:
            return timezone.now().date() > self.service_deadline
        return False
    
    @property
    def progress_rate(self):
        """计算工程进度（简单估算）"""
        if self.actual_start_date and self.estimated_completion_date:
            total_days = (self.estimated_completion_date - self.actual_start_date).days
            if total_days > 0:
                elapsed_days = (timezone.now().date() - self.actual_start_date).days
                return min(100, (elapsed_days / total_days) * 100)
        return 0
