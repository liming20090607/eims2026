"""
造价咨询模块 - 7个子模块数据模型（外键关联架构）
包括：项目信息、任务计划、任务实施、审核成果、收费情况、项目存档、酬劳分配

架构设计：
- CostProjectInfo作为主表，存储项目基础信息
- 其他6个子模块通过project外键关联到CostProjectInfo
- 关联组织管理模块（Department、Personnel）和认证管理模块（User）
- 添加审批流基础字段，为后续审批功能预留
"""
from django.db import models
from django.conf import settings


class CostProjectInfo(models.Model):
    """造价咨询项目信息表"""
    
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, unique=True, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    PROJECT_TYPE_CHOICES = [
        ('budget', '预算'),
        ('settlement', '结算'),
        ('audit', '审核'),
        ('other', '其他'),
    ]
    project_type = models.CharField("项目类型", max_length=20, choices=PROJECT_TYPE_CHOICES, default='budget')
    
    COMPILATION_CATEGORY_CHOICES = [
        ('civil', '土建'),
        ('install', '安装'),
        ('municipal', '市政'),
        ('decoration', '装饰'),
        ('other', '其他'),
    ]
    compilation_category = models.CharField("编制类别", max_length=20, choices=COMPILATION_CATEGORY_CHOICES, default='civil')
    
    REVIEW_CATEGORY_CHOICES = [
        ('initial', '初审'),
        ('intermediate', '中审'),
        ('final', '终审'),
    ]
    review_category = models.CharField("审核类别", max_length=20, choices=REVIEW_CATEGORY_CHOICES, default='initial')
    
    PROJECT_STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('suspended', '已暂停'),
    ]
    project_status = models.CharField("项目状态", max_length=20, choices=PROJECT_STATUS_CHOICES, default='not_started')
    
    # 项目相关方
    client_unit = models.CharField("建设单位", max_length=200, blank=True)
    entrusting_unit = models.CharField("委托单位", max_length=200, blank=True)
    contact_person = models.CharField("联系人", max_length=50, blank=True)
    contact_phone = models.CharField("联系电话", max_length=20, blank=True)
    
    # 时间节点
    submission_time = models.DateField("送审时间", null=True, blank=True)
    start_time = models.DateField("开始时间", null=True, blank=True)
    planned_duration = models.IntegerField("计划工期(天)", default=0)
    planned_completion_time = models.DateField("计划完成时间", null=True, blank=True)
    
    # 金额信息（万元）
    compilation_amount = models.DecimalField("编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    submission_amount = models.DecimalField("送审金额(万元)", max_digits=12, decimal_places=2, default=0)
    approved_amount = models.DecimalField("审定金额(万元)", max_digits=12, decimal_places=2, default=0)
    reduced_amount = models.DecimalField("审减金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 报告信息
    report_time = models.DateField("报告时间", null=True, blank=True)
    
    RESULT_CONFIRM_CHOICES = [
        ('confirmed', '已确认'),
        ('unconfirmed', '未确认'),
        ('pending', '待确认'),
    ]
    result_confirm = models.CharField("结果确认", max_length=20, choices=RESULT_CONFIRM_CHOICES, default='unconfirmed')
    
    # 费用信息（万元）
    total_fee = models.DecimalField("费用总额(万元)", max_digits=12, decimal_places=2, default=0)
    received_fee = models.DecimalField("已收费用(万元)", max_digits=12, decimal_places=2, default=0)
    pending_fee = models.DecimalField("待收费用(万元)", max_digits=12, decimal_places=2, default=0)
    
    FEE_SETTLEMENT_CHOICES = [
        ('settled', '已结清'),
        ('unsettled', '未结清'),
        ('partial', '部分结清'),
    ]
    fee_settlement = models.CharField("费用结清", max_length=20, choices=FEE_SETTLEMENT_CHOICES, default='unsettled')
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "项目信息"
        verbose_name_plural = "项目信息管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
            models.Index(fields=['project_status']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    @property
    def task_plan(self):
        """获取关联的任务计划"""
        return self.cost_task_plans.first()
    
    @property
    def task_implementation(self):
        """获取关联的任务实施"""
        return self.cost_task_implementations.first()
    
    @property
    def review_result(self):
        """获取关联的审核成果"""
        return self.cost_review_results.first()
    
    @property
    def payment_status(self):
        """获取关联的收费情况"""
        return self.cost_payment_statuses.first()
    
    @property
    def archive(self):
        """获取关联的项目存档"""
        return self.cost_archives.first()
    
    @property
    def remuneration(self):
        """获取关联的酬劳分配"""
        return self.cost_remunerations.first()


class CostTaskPlan(models.Model):
    """造价咨询任务计划表 - 通过外键关联CostProjectInfo"""
    
    # ===== 外键关联 =====
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 关联项目主表（核心外键）
    project = models.ForeignKey(
        CostProjectInfo,
        on_delete=models.CASCADE,
        related_name='cost_task_plans',
        verbose_name="关联项目",
        help_text="选择造价咨询项目",
        db_constraint=False
    )
    
    # 冗余字段（从主表关联获取，用于列表显示优化）
    project_code = models.CharField("项目编号", max_length=50, db_index=True, blank=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True, blank=True)
    
    PROJECT_TYPE_CHOICES = [
        ('budget', '预算'),
        ('settlement', '结算'),
        ('audit', '审核'),
        ('other', '其他'),
    ]
    project_type = models.CharField("项目类型", max_length=20, choices=PROJECT_TYPE_CHOICES, default='budget', blank=True)
    
    # 编制信息
    compiler = models.CharField("编制人", max_length=50, blank=True)
    compilation_amount = models.DecimalField("编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 一审计划
    first_reviewer = models.CharField("一审人员", max_length=50, blank=True)
    first_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="一审人员",
        related_name="cost_task_plans_as_first_reviewer",
        help_text="关联人员管理模块",
        db_constraint=False
    )
    first_reviewer_department = models.CharField("一审部门", max_length=100, blank=True)
    first_reviewer_dept = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="一审部门",
        related_name="cost_task_plans_as_first_review",
        help_text="关联部门管理模块",
        db_constraint=False
    )
    first_review_start_time = models.DateField("一审开始时间", null=True, blank=True)
    first_review_planned_duration = models.IntegerField("一审计划工期(天)", default=0)
    first_review_planned_completion = models.DateField("一审计划完成时间", null=True, blank=True)
    
    # 二审计划
    second_reviewer = models.CharField("二审人员", max_length=50, blank=True)
    second_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="二审人员",
        related_name="cost_task_plans_as_second_reviewer",
        help_text="关联人员管理模块",
        db_constraint=False
    )
    second_reviewer_department = models.CharField("二审部门", max_length=100, blank=True)
    second_reviewer_dept = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="二审部门",
        related_name="cost_task_plans_as_second_review",
        help_text="关联部门管理模块",
        db_constraint=False
    )
    second_review_start_time = models.DateField("二审开始时间", null=True, blank=True)
    second_review_planned_duration = models.IntegerField("二审计划工期(天)", default=0)
    second_review_planned_completion = models.DateField("二审计划完成时间", null=True, blank=True)
    
    # 三审计划
    third_reviewer = models.CharField("三审人员", max_length=50, blank=True)
    third_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="三审人员",
        related_name="cost_task_plans_as_third_reviewer",
        help_text="关联人员管理模块",
        db_constraint=False
    )
    third_reviewer_department = models.CharField("三审部门", max_length=100, blank=True)
    third_reviewer_dept = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="三审部门",
        related_name="cost_task_plans_as_third_review",
        help_text="关联部门管理模块",
        db_constraint=False
    )
    third_review_start_time = models.DateField("三审开始时间", null=True, blank=True)
    third_review_planned_duration = models.IntegerField("三审计划工期(天)", default=0)
    third_review_planned_completion = models.DateField("三审计划完成时间", null=True, blank=True)
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    operator = models.CharField("操作人", max_length=50, blank=True)
    
    class Meta:
        verbose_name = "任务计划"
        verbose_name_plural = "任务计划管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class CostTaskImplementation(models.Model):
    """造价咨询任务实施表"""
    
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    PROJECT_TYPE_CHOICES = [
        ('budget', '预算'),
        ('settlement', '结算'),
        ('audit', '审核'),
        ('other', '其他'),
    ]
    project_type = models.CharField("项目类型", max_length=20, choices=PROJECT_TYPE_CHOICES, default='budget')
    
    # 编制信息
    compiler = models.CharField("编制人", max_length=50, blank=True)
    compilation_amount = models.DecimalField("编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 一审实际
    first_review_planned_duration = models.IntegerField("一审计划工期(天)", default=0)
    first_review_planned_completion = models.DateField("一审计划完成时间", null=True, blank=True)
    first_review_actual_completion = models.DateField("一审实际完成时间", null=True, blank=True)
    first_review_actual_duration = models.IntegerField("一审实际工期(天)", default=0)
    first_review_progress_result = models.CharField("一审进度结果", max_length=200, blank=True)
    
    # 二审实际
    second_review_planned_duration = models.IntegerField("二审计划工期(天)", default=0)
    second_review_planned_completion = models.DateField("二审计划完成时间", null=True, blank=True)
    second_review_actual_completion = models.DateField("二审实际完成时间", null=True, blank=True)
    second_review_actual_duration = models.IntegerField("二审实际工期(天)", default=0)
    second_review_progress_result = models.CharField("二审进度结果", max_length=200, blank=True)
    
    # 三审实际
    third_review_planned_duration = models.IntegerField("三审计划工期(天)", default=0)
    third_review_planned_completion = models.DateField("三审计划完成时间", null=True, blank=True)
    third_review_actual_completion = models.DateField("三审实际完成时间", null=True, blank=True)
    third_review_actual_duration = models.IntegerField("三审实际工期(天)", default=0)
    third_review_progress_result = models.CharField("三审进度结果", max_length=200, blank=True)
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "任务实施"
        verbose_name_plural = "任务实施管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class CostReviewResult(models.Model):
    """造价咨询审核成果表"""
    
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    PROJECT_TYPE_CHOICES = [
        ('budget', '预算'),
        ('settlement', '结算'),
        ('audit', '审核'),
        ('other', '其他'),
    ]
    project_type = models.CharField("项目类型", max_length=20, choices=PROJECT_TYPE_CHOICES, default='budget')
    
    # 编制信息
    compiler = models.CharField("编制人", max_length=50, blank=True)
    compilation_amount = models.DecimalField("编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 一审成果
    first_submission = models.DecimalField("一审送审(万元)", max_digits=12, decimal_places=2, default=0)
    first_result = models.CharField("一审结果", max_length=200, blank=True)
    first_reduction = models.DecimalField("一审审减(万元)", max_digits=12, decimal_places=2, default=0)
    first_reduction_rate = models.DecimalField("一审减率(%)", max_digits=6, decimal_places=2, default=0)
    first_review_evaluation = models.CharField("一审评价", max_length=200, blank=True)
    
    # 二审成果
    second_submission = models.DecimalField("二审送审(万元)", max_digits=12, decimal_places=2, default=0)
    second_result = models.CharField("二审结果", max_length=200, blank=True)
    second_reduction_rate = models.DecimalField("二审减率(%)", max_digits=6, decimal_places=2, default=0)
    second_reviewer = models.CharField("二审人员", max_length=50, blank=True)
    second_evaluation = models.CharField("二审评价", max_length=200, blank=True)
    
    # 三审成果
    third_submission = models.DecimalField("三审送审(万元)", max_digits=12, decimal_places=2, default=0)
    third_result = models.CharField("三审结果", max_length=200, blank=True)
    third_reduction_rate = models.DecimalField("三审减率(%)", max_digits=6, decimal_places=2, default=0)
    third_reviewer = models.CharField("三审人员", max_length=50, blank=True)
    third_evaluation = models.CharField("三审评价", max_length=200, blank=True)
    
    # 最终审定
    final_approved_amount = models.DecimalField("审定金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "审核成果"
        verbose_name_plural = "审核成果管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class CostPaymentStatus(models.Model):
    """造价咨询收费情况表"""
    
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    # 开票信息（万元）
    invoice_amount = models.DecimalField("开票金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    INVOICE_STATUS_CHOICES = [
        ('invoiced', '已开票'),
        ('not_invoiced', '未开票'),
        ('partial', '部分开票'),
    ]
    is_invoiced = models.CharField("是否开票", max_length=20, choices=INVOICE_STATUS_CHOICES, default='not_invoiced')
    
    # 业主方收费（万元）
    owner_payable = models.DecimalField("业主方应付(万元)", max_digits=12, decimal_places=2, default=0)
    owner_paid = models.DecimalField("业主方已付(万元)", max_digits=12, decimal_places=2, default=0)
    owner_pending = models.DecimalField("业主方待付(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 施工方收费（万元）
    contractor_payable = models.DecimalField("施工方应付(万元)", max_digits=12, decimal_places=2, default=0)
    contractor_paid = models.DecimalField("施工方已付(万元)", max_digits=12, decimal_places=2, default=0)
    contractor_pending = models.DecimalField("施工方待付(万元)", max_digits=12, decimal_places=2, default=0)
    
    SETTLEMENT_STATUS_CHOICES = [
        ('settled', '已结清'),
        ('unsettled', '未结清'),
        ('partial', '部分结清'),
    ]
    is_settled = models.CharField("是否结清", max_length=20, choices=SETTLEMENT_STATUS_CHOICES, default='unsettled')
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "收费情况"
        verbose_name_plural = "收费情况管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class CostProjectArchive(models.Model):
    """造价咨询项目存档表"""
    
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    # 附件上传函数
    def service_contract_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/service_contract/{filename}'
    
    def submission_material_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/submission/{filename}'
    
    def process_material_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/process/{filename}'
    
    def inspection_record_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/inspection/{filename}'
    
    def audit_report_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/audit_report/{filename}'
    
    def other_document_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/other/{filename}'
    
    # 文档信息
    service_contract = models.FileField("服务合同", upload_to=service_contract_upload_path, blank=True)
    service_contract_type = models.CharField("附件类型", max_length=50, blank=True)
    
    submission_material = models.FileField("送审资料", upload_to=submission_material_upload_path, blank=True)
    submission_material_type = models.CharField("附件类型", max_length=50, blank=True)
    
    process_material = models.FileField("过程资料", upload_to=process_material_upload_path, blank=True)
    process_material_type = models.CharField("附件类型", max_length=50, blank=True)
    
    inspection_record = models.FileField("勘察记录", upload_to=inspection_record_upload_path, blank=True)
    inspection_record_type = models.CharField("附件类型", max_length=50, blank=True)
    
    audit_report = models.FileField("审核报告", upload_to=audit_report_upload_path, blank=True)
    audit_report_type = models.CharField("附件类型", max_length=50, blank=True)
    
    # 业主确认
    owner_confirmation = models.BooleanField("业主确认", default=False)
    
    # 其他文件
    other_document = models.FileField("其他文件", upload_to=other_document_upload_path, blank=True)
    other_document_type = models.CharField("附件类型", max_length=50, blank=True)
    
    # 提交人信息
    submitter = models.CharField("提交人", max_length=50, blank=True)
    submit_time = models.DateTimeField("提交时间", null=True, blank=True)
    archive_time = models.DateTimeField("存档时间", null=True, blank=True)
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "项目存档"
        verbose_name_plural = "项目存档管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class CostRemunerationDistribution(models.Model):
    """造价咨询酬劳分配表 - 主表"""
    
    # 租户字段（多租户数据隔离）
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    # 计算方式选择
    CALC_TYPE_CHOICES = [
        ('compilation', '编制项目'),
        ('review', '审核项目'),
    ]
    calculation_type = models.CharField("计算类型", max_length=20, choices=CALC_TYPE_CHOICES, default='compilation')
    
    CALC_BASE_CHOICES = [
        ('total_cost', '工程总造价'),
        ('reduced_amount', '审减金额'),
    ]
    calculation_base = models.CharField("计算基准", max_length=20, choices=CALC_BASE_CHOICES, default='total_cost')
    
    # 金额信息（万元）
    total_cost = models.DecimalField("工程总造价(万元)", max_digits=12, decimal_places=2, default=0)
    reduced_amount = models.DecimalField("审减金额(万元)", max_digits=12, decimal_places=2, default=0)
    total_remuneration = models.DecimalField("酬劳总额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 计算式（用户手动输入）
    calculation_formula = models.TextField("计算式", blank=True, help_text="例如：工程总造价×0.3%")
    
    # 状态
    DISTRIBUTION_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('distributed', '已分配'),
    ]
    distribution_status = models.CharField("分配状态", max_length=20, choices=DISTRIBUTION_STATUS_CHOICES, default='draft')
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "酬劳分配"
        verbose_name_plural = "酬劳分配管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class CostRemunerationItem(models.Model):
    """造价咨询酬劳分配明细表 - 子表"""
    
    # 关联主表
    distribution = models.ForeignKey(CostRemunerationDistribution, on_delete=models.CASCADE, 
                                     related_name='items', verbose_name="酬劳分配")
    
    # 人员信息
    person_name = models.CharField("人员姓名", max_length=50)
    
    ROLE_CHOICES = [
        ('compiler', '编制人'),
        ('first_reviewer', '一审人员'),
        ('second_reviewer', '二审人员'),
        ('third_reviewer', '三审人员'),
        ('other', '其他人员'),
    ]
    role = models.CharField("角色", max_length=20, choices=ROLE_CHOICES, default='compiler')
    
    # 分配比例及计算
    distribution_percentage = models.DecimalField("分配比例(%)", max_digits=6, decimal_places=2, default=0, help_text="例如：40表示40%")
    calculated_amount = models.DecimalField("计算酬劳(万元)", max_digits=12, decimal_places=2, default=0, help_text="系统自动计算：酬劳总额×分配比例")
    
    # 备注
    remark = models.TextField("备注", blank=True)
    
    # 系统字段
    update_time = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "酬劳分配明细"
        verbose_name_plural = "酬劳分配明细管理"
        ordering = ['role', 'person_name']
        indexes = [
            models.Index(fields=['distribution', 'person_name']),
        ]
    
    def __str__(self):
        return f"{self.person_name} - {self.get_role_display()}"
