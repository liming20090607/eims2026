# E:\EIMS2026\eims_app\models\model_output_payment.py
# 产值回款模型

from django.db import models
from decimal import Decimal
from .model_project_detail import ProjectDetail


class OutputPayment(models.Model):
    """产值回款表 - 用于记录项目的产值和回款情况"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True)
    
    # 关联项目
    project = models.ForeignKey(
        ProjectDetail, 
        on_delete=models.CASCADE, 
        related_name='output_payments',
        verbose_name="项目"
    )
    project_code = models.CharField("项目编号", max_length=50, db_index=True)
    
    # 基础信息
    month = models.CharField("月份", max_length=7)  # 格式：2026-01
    
    # 产值数据（万元）
    monthly_output = models.DecimalField("当月产值 (万元)", max_digits=10, decimal_places=2, default=0)
    cumulative_output = models.DecimalField("累计产值 (万元)", max_digits=10, decimal_places=2, default=0)
    
    # 回款数据（元）
    contract_total = models.DecimalField("合同总额 (元)", max_digits=15, decimal_places=2, default=0)
    cumulative_received = models.DecimalField("累计已收款 (元)", max_digits=15, decimal_places=2, default=0)
    contract_receivable = models.DecimalField("合同应收款 (元)", max_digits=15, decimal_places=2, default=0)
    near_term_receivable = models.DecimalField("近期待收款 (元)", max_digits=15, decimal_places=2, default=0)
    
    # 回款详情
    payment_basis = models.TextField("合同付款依据", blank=True, default='')
    last_payment_situation = models.TextField("上次回款情况", blank=True, default='')
    recent_payment_request = models.TextField("近期请款情况", blank=True, default='')
    actual_payment = models.DecimalField("本月实际回款 (元)", max_digits=15, decimal_places=2, default=0)
    next_month_request = models.TextField("下个月请款", blank=True, default='')
    next_month_plan = models.DecimalField("下月计划收款 (元)", max_digits=15, decimal_places=2, default=0)
    payment_measures = models.TextField("请款措施", blank=True, default='')
    need_assistance = models.TextField("需要协助", blank=True, default='')
    
    # 其他字段
    remark = models.TextField("备注", blank=True, default='')
    payment_date = models.DateField("回款日期", null=True, blank=True)
    payment_method = models.CharField("回款方式", max_length=50, blank=True, default='')
    
    # 冗余字段（便于查询）
    output_amount = models.DecimalField("当月产值 (万元)", max_digits=10, decimal_places=2, default=0)
    payment_amount = models.DecimalField("本月实际回款 (元)", max_digits=15, decimal_places=2, default=0)
    
    # 操作信息
    operator = models.CharField("操作人", max_length=50, blank=True, default='')
    
    # 系统字段
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        ordering = ['-month', '-create_time']
        indexes = [
            models.Index(fields=['project_code', 'month']),
            models.Index(fields=['project', 'month']),
        ]
        verbose_name = "产值回款"
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.project_code} - {self.month} - 产值：{self.monthly_output}万 - 回款：{self.actual_payment}元"
