from django.db import models
from django.conf import settings
import os
import uuid


class SealApprovalManager(models.Manager):
    """用印审批查询集"""
    pass


class SealApproval(models.Model):
    """用印审批表 - 存储用印审批主信息"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True)
    
    # 审批状态选择
    APPROVAL_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('reviewing', '审核中'),
        ('approved', '已通过'),
        ('rejected', '已退回'),
        ('cancelled', '已撤销'),
    ]
    
    # 印章类型选择
    SEAL_TYPE_CHOICES = [
        ('official_seal', '公章'),
        ('legal_representative_seal', '法人章'),
        ('legal_representative_signature', '法人签字章'),
        ('professional_seal', '执业印章'),
        ('contract_seal', '合同专用章'),
        ('finance_seal', '财务专用章'),
        ('invoice_seal', '发票专用章'),
        ('other', '其他印章'),
    ]
    
    # 基本信息
    title = models.CharField("审批标题", max_length=200)
    
    # 申请信息
    department = models.ForeignKey(
        'Department', 
        verbose_name="申请部门", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='seal_approvals'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="申请人", 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='seal_approvals'
    )
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="发起人", 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='initiated_seal_approvals',
        help_text="审批流程的发起人"
    )
    initiation_time = models.DateTimeField("发起时间", null=True, blank=True, help_text="审批流程的初始提交时间")
    
    # 印章信息
    seal_type = models.CharField("印章名称", max_length=50, choices=SEAL_TYPE_CHOICES)
    seal_count = models.IntegerField("盖章数量", default=1, help_text="需要盖章的份数")
    
    # 文件信息
    document_name = models.CharField("文件名称", max_length=200)
    document_type = models.CharField("文件类型", max_length=50, blank=True, help_text="如：合同、报告、证明等")
    
    # 关联项目（可选）
    project_name = models.CharField("关联项目", max_length=200, blank=True)
    project_code = models.CharField("项目编号", max_length=50, blank=True)
    
    # 用印用途
    usage_purpose = models.TextField("用印用途", help_text="说明用印的具体用途")
    
    # 审批状态
    status = models.CharField("审批状态", max_length=20, choices=APPROVAL_STATUS_CHOICES, default='draft')
    current_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="当前审批人", 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='seal_approvals_to_handle'
    )
    
    # ===== 审批流程配置 =====
    APPROVAL_FLOW_TYPE_CHOICES = [
        ('user_selected', '由我选择审批人'),
        ('system_assigned', '由系统自动指派'),
    ]
    approval_flow_type = models.CharField("审批流程类型", max_length=20, choices=APPROVAL_FLOW_TYPE_CHOICES, default='system_assigned')
    
    # 用户选择的审批信息
    selected_department = models.ForeignKey(
        'Department', 
        verbose_name="选择的审批部门", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='selected_seal_approvals'
    )
    selected_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="选择的审批人", 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='selected_seal_approvals'
    )
    
    # 系统指派的审批信息
    auto_assigned_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="系统指派的审批人", 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='auto_assigned_seal_approvals'
    )
    
    # 审批级别（用于多级审批）
    approval_level = models.IntegerField("当前审批级别", default=1, help_text="1=部门级，2=上级")
    max_approval_level = models.IntegerField("最大审批级别", default=2, help_text="默认 2 级审批")
    
    # 备注
    remark = models.TextField("备注", blank=True)
    
    # 时间戳
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    submitted_at = models.DateTimeField("提交时间", null=True, blank=True)
    approved_at = models.DateTimeField("审批通过时间", null=True, blank=True)
    
    # 软删除
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SealApprovalManager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "用印审批"
        verbose_name_plural = "用印审批"
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @staticmethod
    def auto_assign_approver(department, approval_level=1):
        """
        系统自动指派审批人
        :param department: 发起部门
        :param approval_level: 审批级别 (1=部门级，2=上级)
        :return: 指派的审批人 User 对象
        """
        from .model_approval_flow import DepartmentManager
        
        if not department:
            return None
        
        # 尝试查找指定级别的审批人
        # 优先查找主要责任人 (is_primary=True)
        approver = DepartmentManager.objects.filter(
            department=department,
            approval_level=approval_level,
            is_active=True
        ).order_by('-is_primary', 'id').first()
        
        if approver:
            return approver.user
        
        # 如果没有找到，尝试查找上级领导
        if approval_level == 1:
            parent_dept = department.parent
            if parent_dept:
                return DepartmentManager.auto_assign_approver(parent_dept, approval_level=1)
        
        return None
    
    def assign_current_approver(self):
        """
        为当前审批单指派审批人
        :return: 被指派的审批人
        """
        if self.approval_flow_type == 'user_selected':
            # 用户选择模式
            if self.selected_approver:
                self.current_approver = self.selected_approver
            elif self.selected_department:
                # 如果只选择了部门，从该部门找主管
                self.current_approver = self.auto_assign_approver(self.selected_department, self.approval_level)
        else:
            # 系统指派模式
            self.current_approver = self.auto_assign_approver(self.department, self.approval_level)
        
        if self.current_approver:
            self.status = 'reviewing'
        
        return self.current_approver


class SealAttachment(models.Model):
    """用印审批附件表 - 存储上传的文档"""
    
    FILE_TYPE_CHOICES = [
        ('document', '文件原件'),
        ('attachment', '附件材料'),
        ('other', '其他资料'),
    ]
    
    approval = models.ForeignKey(
        SealApproval, 
        verbose_name="所属审批", 
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField("上传文件", upload_to='seal_approvals/%Y/%m/')
    file_type = models.CharField("文件类型", max_length=20, choices=FILE_TYPE_CHOICES, default='document')
    file_name = models.CharField("文件名", max_length=255)
    file_size = models.IntegerField("文件大小 (字节)", default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="上传人", 
        on_delete=models.SET_NULL, 
        null=True
    )
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "用印附件"
        verbose_name_plural = "用印附件"
    
    def __str__(self):
        return self.file_name
    
    def save(self, *args, **kwargs):
        """保存时自动填充文件名和大小"""
        if self.file:
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """删除时同时删除文件"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class SealApprovalRecord(models.Model):
    """用印审批记录表 - 存储审批历史记录"""
    
    ACTION_CHOICES = [
        ('submit', '提交'),
        ('approve', '同意'),
        ('reject', '退回'),
        ('cancel', '撤销'),
        ('comment', '评论'),
    ]
    
    approval = models.ForeignKey(
        SealApproval, 
        verbose_name="所属审批", 
        on_delete=models.CASCADE,
        related_name='approval_records'
    )
    action = models.CharField("操作类型", max_length=20, choices=ACTION_CHOICES)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="操作人", 
        on_delete=models.SET_NULL, 
        null=True
    )
    comment = models.TextField("审批意见", blank=True)
    created_at = models.DateTimeField("操作时间", auto_now_add=True)
    
    # 转发相关字段
    next_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="下一步审批人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_seal_approval_records'
    )
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "用印审批记录"
        verbose_name_plural = "用印审批记录"
    
    def __str__(self):
        return f"{self.approval.title} - {self.operator.username} - {self.get_action_display()}"
