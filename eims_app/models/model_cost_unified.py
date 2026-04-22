"""
造价咨询模块 - 统一项目表模型（单表架构）

设计理念：
- 将所有7个子模块的字段合并到一个表中
- 通过字段前缀区分不同业务模块
- 简化数据模型，避免外键同步问题
- 提高查询性能，减少JOIN操作
"""
from django.db import models
from django.conf import settings


class CostProjectUnified(models.Model):
    """
    造价咨询统一项目表
    
    包含原7个子模块的所有字段：
    1. 项目信息 (CostProjectInfo)
    2. 任务计划 (CostTaskPlan)
    3. 任务实施 (CostTaskImplementation)
    4. 审核成果 (CostReviewResult)
    5. 收费情况 (CostPaymentStatus)
    6. 项目存档 (CostProjectArchive)
    7. 酬劳分配 (CostRemunerationDistribution)
    """
    
    # ========================================================================
    # 系统字段
    # ========================================================================
    tenant = models.ForeignKey(
        'Tenant', 
        on_delete=models.PROTECT,
        null=True, 
        blank=True,
        verbose_name='所属公司',
        db_index=True,
        db_constraint=False
    )
    
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    operator = models.CharField("操作人", max_length=50, blank=True)
    
    # ========================================================================
    # 审批流字段
    # ========================================================================
    APPROVAL_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending_approval', '待审批'),
        ('approved', '已审批'),
        ('rejected', '已退回'),
        ('cancelled', '已撤销'),
    ]
    
    approval_status = models.CharField(
        "审批状态", 
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='draft', 
        db_index=True
    )
    
    current_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="当前审批人",
        db_constraint=False
    )
    
    approval_department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="审批部门",
        db_constraint=False
    )
    
    approval_level = models.IntegerField("审批级别", default=1)
    submit_time = models.DateTimeField("提交审批时间", null=True, blank=True)
    approval_time = models.DateTimeField("审批时间", null=True, blank=True)
    approval_remark = models.TextField("审批意见", blank=True)
    
    # ========================================================================
    # 模块1: 项目信息 (来自原 CostProjectInfo)
    # ========================================================================
    
    # 基础信息
    project_code = models.CharField("项目编号", max_length=50, unique=True, db_index=True)
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    PROJECT_TYPE_CHOICES = [
        ('budget_compilation', '预算编制'),
        ('settlement_compilation', '结算编制'),
        ('budget_review', '预算审核'),
        ('settlement_review', '结算审核'),
        ('other', '其他'),
    ]
    project_type = models.CharField("项目类型", max_length=30, choices=PROJECT_TYPE_CHOICES, default='budget_compilation', blank=True)
    
    MAJOR_CHOICES = [
        ('architecture', '建筑'),
        ('hydroelectric', '水电'),
        ('landscape', '园林'),
        ('municipal', '市政'),
        ('electric_power', '电力'),
        ('other', '其他'),
    ]
    compilation_category = models.CharField("专业", max_length=50, blank=True)
    
    REVIEW_CATEGORY_CHOICES = [
        ('initial', '初审'),
        ('intermediate', '中审'),
        ('final', '终审'),
    ]
    review_category = models.CharField("审核类别", max_length=20, choices=REVIEW_CATEGORY_CHOICES, blank=True, default='')
    
    PROJECT_STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('suspended', '已暂停'),
    ]
    project_status = models.CharField("项目状态", max_length=20, choices=PROJECT_STATUS_CHOICES, default='not_started', blank=True)
    
    # 项目相关方
    client_unit = models.CharField("建设单位", max_length=200, blank=True)
    entrusting_unit = models.CharField("委托单位", max_length=200, blank=True)
    contact_person = models.CharField("联系人", max_length=50, blank=True)
    contact_phone = models.CharField("联系电话", max_length=20, blank=True)
    
    # 项目负责人
    project_manager_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="项目负责人",
        related_name="cost_unified_as_manager",
        db_constraint=False
    )
    
    # 时间节点
    submission_time = models.DateField("送审时间", null=True, blank=True)
    start_time = models.DateField("开始时间", null=True, blank=True)
    planned_duration = models.IntegerField("计划工期(天)", default=0, blank=True)
    planned_completion_time = models.DateField("计划完成时间", null=True, blank=True)
    
    # 金额信息
    compilation_amount = models.DecimalField("编制金额(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    submission_amount = models.DecimalField("送审金额(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    approved_amount = models.DecimalField("审定金额(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    reduced_amount = models.DecimalField("审减金额(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    
    # 报告信息
    report_time = models.DateField("报告时间", null=True, blank=True)
    completion_time = models.DateField("完成时间", null=True, blank=True)
    
    RESULT_CONFIRM_CHOICES = [
        ('confirmed', '已确认'),
        ('unconfirmed', '未确认'),
        ('pending', '待确认'),
    ]
    result_confirm = models.CharField("结果确认", max_length=20, choices=RESULT_CONFIRM_CHOICES, default='unconfirmed', blank=True)
    
    # 费用信息
    total_fee = models.DecimalField("费用总额(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    received_fee = models.DecimalField("已收费用(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    pending_fee = models.DecimalField("待收费用(万元)", max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    
    FEE_SETTLEMENT_CHOICES = [
        ('settled', '已结清'),
        ('unsettled', '未结清'),
        ('partial', '部分结清'),
    ]
    fee_settlement = models.CharField("费用结清", max_length=20, choices=FEE_SETTLEMENT_CHOICES, default='unsettled', blank=True)
    
    remark = models.TextField("备注", blank=True)
    
    # ========================================================================
    # 模块2: 任务计划 (来自原 CostTaskPlan)
    # ========================================================================
    
    # 编制信息
    plan_compiler = models.CharField("计划-编制人", max_length=50, blank=True)
    plan_compiler_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="计划-编制人员",
        related_name="cost_unified_as_plan_compiler",
        db_constraint=False
    )
    plan_compilation_amount = models.DecimalField("计划-编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 一审计划
    plan_first_reviewer = models.CharField("计划-一审人员", max_length=50, blank=True)
    plan_first_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="计划-一审人员",
        related_name="cost_unified_as_plan_first_reviewer",
        db_constraint=False
    )
    plan_first_reviewer_department = models.CharField("计划-一审部门", max_length=100, blank=True)
    plan_first_review_start_time = models.DateField("计划-一审开始时间", null=True, blank=True)
    plan_first_review_planned_duration = models.IntegerField("计划-一审计划工期(天)", default=0)
    plan_first_review_planned_completion = models.DateField("计划-一审计划完成时间", null=True, blank=True)
    
    # 二审计划
    plan_second_reviewer = models.CharField("计划-二审人员", max_length=50, blank=True)
    plan_second_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="计划-二审人员",
        related_name="cost_unified_as_plan_second_reviewer",
        db_constraint=False
    )
    plan_second_reviewer_department = models.CharField("计划-二审部门", max_length=100, blank=True)
    plan_second_review_start_time = models.DateField("计划-二审开始时间", null=True, blank=True)
    plan_second_review_planned_duration = models.IntegerField("计划-二审计划工期(天)", default=0)
    plan_second_review_planned_completion = models.DateField("计划-二审计划完成时间", null=True, blank=True)
    
    # 三审计划
    plan_third_reviewer = models.CharField("计划-三审人员", max_length=50, blank=True)
    plan_third_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="计划-三审人员",
        related_name="cost_unified_as_plan_third_reviewer",
        db_constraint=False
    )
    plan_third_reviewer_department = models.CharField("计划-三审部门", max_length=100, blank=True)
    plan_third_review_start_time = models.DateField("计划-三审开始时间", null=True, blank=True)
    plan_third_review_planned_duration = models.IntegerField("计划-三审计划工期(天)", default=0)
    plan_third_review_planned_completion = models.DateField("计划-三审计划完成时间", null=True, blank=True)
    
    # ========================================================================
    # 模块3: 任务实施 (来自原 CostTaskImplementation)
    # ========================================================================
    
    # 编制实际
    impl_compiler = models.CharField("实施-编制人", max_length=50, blank=True)
    impl_compiler_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="实施-编制人员",
        related_name="cost_unified_as_impl_compiler",
        db_constraint=False
    )
    impl_compilation_amount = models.DecimalField("实施-编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    impl_compilation_start = models.DateField("实施-编制开始时间", null=True, blank=True)
    impl_compilation_end = models.DateField("实施-编制完成时间", null=True, blank=True)
    impl_compilation_actual_duration = models.IntegerField("实施-编制实际工期(天)", default=0)
    
    # 一审实际
    impl_first_reviewer = models.CharField("实施-一审人员", max_length=50, blank=True)
    impl_first_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="实施-一审人员",
        related_name="cost_unified_as_impl_first_reviewer",
        db_constraint=False
    )
    impl_first_review_start = models.DateField("实施-一审开始时间", null=True, blank=True)
    impl_first_review_end = models.DateField("实施-一审完成时间", null=True, blank=True)
    impl_first_review_actual_duration = models.IntegerField("实施-一审实际工期(天)", default=0)
    impl_first_review_progress_result = models.CharField("实施-一审进度结果", max_length=200, blank=True)
    
    # 二审实际
    impl_second_reviewer = models.CharField("实施-二审人员", max_length=50, blank=True)
    impl_second_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="实施-二审人员",
        related_name="cost_unified_as_impl_second_reviewer",
        db_constraint=False
    )
    impl_second_review_start = models.DateField("实施-二审开始时间", null=True, blank=True)
    impl_second_review_end = models.DateField("实施-二审完成时间", null=True, blank=True)
    impl_second_review_actual_duration = models.IntegerField("实施-二审实际工期(天)", default=0)
    impl_second_review_progress_result = models.CharField("实施-二审进度结果", max_length=200, blank=True)
    
    # 三审实际
    impl_third_reviewer = models.CharField("实施-三审人员", max_length=50, blank=True)
    impl_third_reviewer_personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="实施-三审人员",
        related_name="cost_unified_as_impl_third_reviewer",
        db_constraint=False
    )
    impl_third_review_start = models.DateField("实施-三审开始时间", null=True, blank=True)
    impl_third_review_end = models.DateField("实施-三审完成时间", null=True, blank=True)
    impl_third_review_actual_duration = models.IntegerField("实施-三审实际工期(天)", default=0)
    impl_third_review_progress_result = models.CharField("实施-三审进度结果", max_length=200, blank=True)
    
    IMPLEMENTATION_STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('delayed', '已延期'),
    ]
    implementation_status = models.CharField("实施状态", max_length=20, choices=IMPLEMENTATION_STATUS_CHOICES, default='not_started', blank=True)
    
    # ========================================================================
    # 模块4: 审核成果 (来自原 CostReviewResult)
    # ========================================================================
    
    # 编制信息
    review_compiler = models.CharField("审核-编制人", max_length=50, blank=True)
    review_compilation_amount = models.DecimalField("审核-编制金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 一审成果
    review_first_submission = models.DecimalField("审核-一审送审(万元)", max_digits=12, decimal_places=2, default=0)
    review_first_result = models.CharField("审核-一审结果", max_length=200, blank=True)
    review_first_reduction = models.DecimalField("审核-一审审减(万元)", max_digits=12, decimal_places=2, default=0)
    review_first_reduction_rate = models.DecimalField("审核-一审减率(%)", max_digits=6, decimal_places=2, default=0)
    review_first_review_evaluation = models.CharField("审核-一审评价", max_length=200, blank=True)
    
    # 二审成果
    review_second_submission = models.DecimalField("审核-二审送审(万元)", max_digits=12, decimal_places=2, default=0)
    review_second_result = models.CharField("审核-二审结果", max_length=200, blank=True)
    review_second_reduction = models.DecimalField("审核-二审审减(万元)", max_digits=12, decimal_places=2, default=0)
    review_second_reduction_rate = models.DecimalField("审核-二审减率(%)", max_digits=6, decimal_places=2, default=0)
    review_second_reviewer = models.CharField("审核-二审人员", max_length=50, blank=True)
    review_second_evaluation = models.CharField("审核-二审评价", max_length=200, blank=True)
    
    # 三审成果
    review_third_submission = models.DecimalField("审核-三审送审(万元)", max_digits=12, decimal_places=2, default=0)
    review_third_result = models.CharField("审核-三审结果", max_length=200, blank=True)
    review_third_reduction = models.DecimalField("审核-三审审减(万元)", max_digits=12, decimal_places=2, default=0)
    review_third_reduction_rate = models.DecimalField("审核-三审减率(%)", max_digits=6, decimal_places=2, default=0)
    review_third_reviewer = models.CharField("审核-三审人员", max_length=50, blank=True)
    review_third_evaluation = models.CharField("审核-三审评价", max_length=200, blank=True)
    
    # 最终审定
    review_final_approved_amount = models.DecimalField("审核-审定金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # ========================================================================
    # 模块5: 收费情况 (来自原 CostPaymentStatus)
    # ========================================================================
    
    # 开票信息
    payment_invoice_amount = models.DecimalField("收费-开票金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    INVOICE_STATUS_CHOICES = [
        ('invoiced', '已开票'),
        ('not_invoiced', '未开票'),
        ('partial', '部分开票'),
    ]
    payment_is_invoiced = models.CharField("收费-是否开票", max_length=20, choices=INVOICE_STATUS_CHOICES, default='not_invoiced')
    
    # 业主方收费
    payment_owner_payable = models.DecimalField("收费-业主方应付(万元)", max_digits=12, decimal_places=2, default=0)
    payment_owner_paid = models.DecimalField("收费-业主方已付(万元)", max_digits=12, decimal_places=2, default=0)
    payment_owner_pending = models.DecimalField("收费-业主方待付(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 施工方收费
    payment_contractor_payable = models.DecimalField("收费-施工方应付(万元)", max_digits=12, decimal_places=2, default=0)
    payment_contractor_paid = models.DecimalField("收费-施工方已付(万元)", max_digits=12, decimal_places=2, default=0)
    payment_contractor_pending = models.DecimalField("收费-施工方待付(万元)", max_digits=12, decimal_places=2, default=0)
    
    SETTLEMENT_STATUS_CHOICES = [
        ('settled', '已结清'),
        ('unsettled', '未结清'),
        ('partial', '部分结清'),
    ]
    payment_is_settled = models.CharField("收费-是否结清", max_length=20, choices=SETTLEMENT_STATUS_CHOICES, default='unsettled')
    
    # ========================================================================
    # 模块6: 项目存档 (来自原 CostProjectArchive)
    # ========================================================================
    
    ARCHIVE_STATUS_CHOICES = [
        ('not_archived', '未归档'),
        ('archiving', '归档中'),
        ('pending_receive', '待接收'),
        ('rejected', '退回'),
        ('archived', '已归档'),
    ]
    archive_status = models.CharField("存档-归档状态", max_length=20, choices=ARCHIVE_STATUS_CHOICES, default='not_archived')
    
    archive_electronic = models.BooleanField("存档-电子档案", default=False)
    archive_paper = models.BooleanField("存档-纸质档案", default=False)
    archive_complete = models.BooleanField("存档-归档完整", default=False)
    archive_location = models.CharField("存档-存放位置", max_length=200, blank=True)
    archive_date = models.DateField("存档-归档日期", null=True, blank=True)
    archive_remark = models.TextField("存档-备注", blank=True)
    
    # ===== 附件上传函数 =====
    def archive_service_contract_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/service_contract/{filename}'
    
    def archive_submission_material_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/submission/{filename}'
    
    def archive_process_material_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/process/{filename}'
    
    def archive_inspection_record_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/inspection/{filename}'
    
    def archive_audit_report_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/audit_report/{filename}'
    
    def archive_other_document_upload_path(instance, filename):
        return f'cost_archives/{instance.project_code}/other/{filename}'
    
    # ===== 文档信息 =====
    archive_service_contract = models.FileField("存档-服务合同", upload_to=archive_service_contract_upload_path, blank=True)
    archive_service_contract_type = models.CharField("存档-合同附件类型", max_length=50, blank=True)
    
    archive_submission_material = models.FileField("存档-送审资料", upload_to=archive_submission_material_upload_path, blank=True)
    archive_submission_material_type = models.CharField("存档-送审附件类型", max_length=50, blank=True)
    
    archive_process_material = models.FileField("存档-过程资料", upload_to=archive_process_material_upload_path, blank=True)
    archive_process_material_type = models.CharField("存档-过程附件类型", max_length=50, blank=True)
    
    archive_inspection_record = models.FileField("存档-勘察记录", upload_to=archive_inspection_record_upload_path, blank=True)
    archive_inspection_record_type = models.CharField("存档-勘察附件类型", max_length=50, blank=True)
    
    archive_audit_report = models.FileField("存档-审核报告", upload_to=archive_audit_report_upload_path, blank=True)
    archive_audit_report_type = models.CharField("存档-报告附件类型", max_length=50, blank=True)
    
    archive_other_document = models.FileField("存档-其他文件", upload_to=archive_other_document_upload_path, blank=True)
    archive_other_document_type = models.CharField("存档-其他附件类型", max_length=50, blank=True)
    
    # ========================================================================
    # 模块7: 酬劳分配 (来自原 CostRemunerationDistribution)
    # ========================================================================
    
    CALC_TYPE_CHOICES = [
        ('compilation', '编制项目'),
        ('review', '审核项目'),
    ]
    remuneration_calculation_type = models.CharField("酬劳-计算类型", max_length=20, choices=CALC_TYPE_CHOICES, default='compilation')
    
    CALC_BASE_CHOICES = [
        ('total_cost', '工程总造价'),
        ('reduced_amount', '审减金额'),
    ]
    remuneration_calculation_base = models.CharField("酬劳-计算基准", max_length=20, choices=CALC_BASE_CHOICES, default='total_cost')
    
    remuneration_total_cost = models.DecimalField("酬劳-工程总造价(万元)", max_digits=12, decimal_places=2, default=0)
    remuneration_reduced_amount = models.DecimalField("酬劳-审减金额(万元)", max_digits=12, decimal_places=2, default=0)
    remuneration_total_remuneration = models.DecimalField("酬劳-酬劳总额(万元)", max_digits=12, decimal_places=2, default=0)
    
    remuneration_calculation_formula = models.TextField("酬劳-计算式", blank=True, help_text="例如：工程总造价×0.3%")
    
    DISTRIBUTION_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('distributed', '已分配'),
    ]
    remuneration_distribution_status = models.CharField("酬劳-分配状态", max_length=20, choices=DISTRIBUTION_STATUS_CHOICES, default='draft')
    
    # 分配比例
    remuneration_compiler_ratio = models.DecimalField("酬劳-编制人比例", max_digits=5, decimal_places=2, default=0)
    remuneration_first_reviewer_ratio = models.DecimalField("酬劳-一审人比例", max_digits=5, decimal_places=2, default=0)
    remuneration_second_reviewer_ratio = models.DecimalField("酬劳-二审人比例", max_digits=5, decimal_places=2, default=0)
    remuneration_third_reviewer_ratio = models.DecimalField("酬劳-三审人比例", max_digits=5, decimal_places=2, default=0)
    
    # ========================================================================
    # Meta配置
    # ========================================================================
    
    class Meta:
        verbose_name = "造价咨询项目"
        verbose_name_plural = "造价咨询项目管理"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
            models.Index(fields=['project_status']),
            models.Index(fields=['approval_status']),
            models.Index(fields=['tenant']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    def save(self, *args, **kwargs):
        """保存时自动设置操作人"""
        if not self.pk and hasattr(self, '_request'):
            request = self._request
            if hasattr(request, 'user') and request.user.is_authenticated:
                self.operator = request.user.username
        super().save(*args, **kwargs)


# ============================================================================
# 酬劳分配明细表（保留为独立表，因为是一对多关系）
# ============================================================================

class CostUnifiedRemunerationItem(models.Model):
    """造价咨询统一表-酬劳分配明细表"""
    
    # 关联统一项目表
    project = models.ForeignKey(
        CostProjectUnified,
        on_delete=models.CASCADE,
        related_name='remuneration_items',
        verbose_name="关联项目",
        db_constraint=False
    )
    
    # 人员信息
    person_name = models.CharField("姓名", max_length=50)
    person_id_card = models.CharField("身份证号", max_length=18, blank=True)
    
    ROLE_CHOICES = [
        ('compiler', '编制人'),
        ('first_reviewer', '一审人'),
        ('second_reviewer', '二审人'),
        ('third_reviewer', '三审人'),
        ('other', '其他'),
    ]
    role = models.CharField("角色", max_length=20, choices=ROLE_CHOICES)
    
    # 分配信息
    ratio = models.DecimalField("分配比例(%)", max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField("分配金额(万元)", max_digits=12, decimal_places=2, default=0)
    
    # 系统字段
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "酬劳分配明细"
        verbose_name_plural = "酬劳分配明细管理"
        ordering = ['role', 'person_name']
        indexes = [
            models.Index(fields=['project', 'person_name']),
        ]
    
    def __str__(self):
        return f"{self.person_name} - {self.get_role_display()}"
