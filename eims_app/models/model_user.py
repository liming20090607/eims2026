from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='默认公司',
                               help_text='用户默认所属公司，用于数据隔离和登录默认选择')
    real_name = models.CharField(max_length=50, verbose_name='姓名', blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='性别', blank=True)
    birthday = models.DateField(verbose_name='生日', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='手机号', blank=True)
    wechat = models.CharField(max_length=50, verbose_name='微信号', blank=True)
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return self.user.username


class UserTenantRelation(models.Model):
    """用户-公司关联表 - 支持一个用户在多家公司任职"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, verbose_name='公司')
    is_primary = models.BooleanField(default=False, verbose_name='是否主公司',
                                     help_text='每个用户只能有一个主公司')
    remark = models.CharField(max_length=200, blank=True, verbose_name='备注',
                             help_text='如：全职/兼职/顾问等')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '用户公司关联'
        verbose_name_plural = '用户公司关联管理'
        unique_together = ['user', 'tenant']  # 同一用户在同一公司只能有一条记录
        indexes = [
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['tenant']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tenant.name}"
    
    def save(self, *args, **kwargs):
        """确保每个用户只有一个主公司"""
        if self.is_primary:
            # 将该用户的其他关联记录设为非主公司
            UserTenantRelation.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class ProjectReporter(models.Model):
    """项目填报人员关联表 - 分配项目给指定人员填报"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='填报人员')
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, verbose_name='关联项目')
    
    REPORT_PERIOD_CHOICES = [
        ('monthly', '月度'),
        ('weekly', '周度'),
        ('quarterly', '季度'),
    ]
    report_period = models.CharField(max_length=20, choices=REPORT_PERIOD_CHOICES, default='monthly', verbose_name='填报周期')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '项目填报人员'
        verbose_name_plural = '项目填报人员管理'
        unique_together = ['user', 'project']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.project_name}"


class MonthlyReport(models.Model):
    """月度填报记录 - 记录每月填报状态和内容"""
    
    REPORT_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('overdue', '已逾期'),
        ('pending_review', '待总监审核'),
        ('pending_approval', '待管理员审批'),
        ('approved', '已批准'),
        ('rejected', '已退回'),
    ]
    
    # 基础信息
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='填报人')
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, verbose_name='填报项目')
    project_code = models.CharField(max_length=50, verbose_name='项目编号', db_index=True, blank=True)
    
    report_year = models.IntegerField(verbose_name='填报年份')
    report_month = models.CharField(max_length=7, verbose_name='填报月份', help_text='格式：YYYY-MM')
    
    # 填报状态
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='draft', verbose_name='填报状态')
    
    # ===== 项目进度信息 =====
    project_progress = models.TextField(verbose_name='项目进度说明', blank=True, default='',
                                        help_text='描述当前项目进度情况')
    current_status = models.CharField(max_length=20, verbose_name='当前状态', 
                                      choices=[
                                          ('not_started', '未开工'),
                                          ('normal_construction', '正常施工'),
                                          ('stopped', '在停工'),
                                          ('completed', '已完工')
                                      ], blank=True, default='')
    
    # ===== 产值信息 =====
    last_month_cumulative_output = models.DecimalField(max_digits=15, decimal_places=2, 
                                                       default=0, verbose_name='上月累计产值 (万元)',
                                                       help_text='截止到上月的累计产值')
    monthly_output_value = models.DecimalField(max_digits=15, decimal_places=2, 
                                               default=0, verbose_name='本月完成产值 (万元)',
                                               help_text='本月实际完成的产值金额')
    current_cumulative_output = models.DecimalField(max_digits=15, decimal_places=2, 
                                                    default=0, verbose_name='本月累计产值 (万元)',
                                                    help_text='截止到本月的累计产值（自动计算）')
    
    # ===== 回款信息 =====
    last_month_cumulative_payment = models.DecimalField(max_digits=15, decimal_places=2, 
                                                        default=0, verbose_name='上月累计回款 (元)',
                                                        help_text='截止到上月的累计回款')
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2, 
                                          default=0, verbose_name='本月回款金额 (元)',
                                          help_text='本月实际收到的款项')
    current_cumulative_payment = models.DecimalField(max_digits=15, decimal_places=2, 
                                                     default=0, verbose_name='本月累计回款 (元)',
                                                     help_text='截止到本月的累计回款（自动计算）')
    payment_description = models.TextField(verbose_name='回款情况说明', blank=True, default='')
    
    # ===== 人员变动 =====
    personnel_changes = models.TextField(verbose_name='本月人员变动', blank=True, default='')
    total_personnel = models.IntegerField(verbose_name='当前总人数', default=0)
    
    # ===== 请款情况 =====
    current_payment_request = models.DecimalField(max_digits=15, decimal_places=2, 
                                                  default=0, verbose_name='本月正在请款金额 (元)',
                                                  help_text='本月正在申请的款项金额')
    payment_progress = models.CharField(max_length=200, verbose_name='本月请款进度', blank=True, default='',
                                        help_text='如：已提交申请/审批中/已到账')
    payment_issues = models.TextField(verbose_name='问题及建议', blank=True, default='',
                                      help_text='需要协调的问题和建议')
    
    # ===== 下月工作计划 =====
    next_month_plan_amount = models.DecimalField(max_digits=15, decimal_places=2, 
                                                 default=0, verbose_name='下月请款金额 (元)',
                                                 help_text='计划下月申请的款项金额')
    next_month_plan_detail = models.TextField(verbose_name='具体请款计划', blank=True, default='',
                                              help_text='详细的请款计划和安排')
    next_month_assistance = models.TextField(verbose_name='需要的协助', blank=True, default='',
                                             help_text='需要公司或领导协助的事项')
    
    # ===== 时间节点 =====
    should_submit_date = models.DateField(verbose_name='应提交日期', null=True, blank=True,
                                          help_text='每月 25 日为截止日期')
    actual_submit_date = models.DateField(verbose_name='实际提交日期', null=True, blank=True)
    
    # 审核相关（保留原有字段）
    submit_time = models.DateTimeField(verbose_name='提交时间', null=True, blank=True)
    approve_time = models.DateTimeField(verbose_name='审核时间', null=True, blank=True)
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='approved_reports', verbose_name='审核人')
    reject_reason = models.TextField(verbose_name='退回原因', blank=True, default='')
    
    # 时间戳
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '月度报告'
        verbose_name_plural = '月度报告管理'
        unique_together = ['project', 'report_year', 'report_month']
        ordering = ['-report_year', '-report_month', '-create_time']
        indexes = [
            models.Index(fields=['report_year', 'report_month']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.project.project_name} - {self.report_year}年{self.report_month}月 - {self.get_status_display()}"
    
    def is_overdue(self):
        """检查是否已逾期"""
        from datetime import date
        if self.status == 'submitted':
            return False
        return date.today() > self.should_submit_date
    
    def days_until_due(self):
        """计算距离截止日期还有多少天"""
        from datetime import date
        today = date.today()
        delta = self.should_submit_date - today
        return delta.days
    
    def save(self, *args, **kwargs):
        # 自动设置项目编号
        if not self.project_code and self.project:
            self.project_code = self.project.project_code
        
        # 如果没有设置应提交日期，默认为当月 25 日
        if not self.should_submit_date:
            from datetime import date
            # report_month 是字符串格式 "YYYY-MM"，需要解析
            if self.report_month and '-' in str(self.report_month):
                year, month = map(int, self.report_month.split('-'))
                self.should_submit_date = date(year, month, 25)
            else:
                # 如果是数字或其他格式，直接作为月份
                self.should_submit_date = date(self.report_year, int(self.report_month), 25)
        
        # 检查是否逾期
        if self.is_overdue() and self.status == 'draft':
            self.status = 'overdue'
        
        super().save(*args, **kwargs)
