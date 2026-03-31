from django.db import models
from django.conf import settings


class DepartmentManager(models.Model):
    """部门主管关系表 - 定义各部门的主管和领导"""
    
    ROLE_CHOICES = [
        ('department_manager', '部门主管'),
        ('senior_leader', '上级领导'),
        ('finance_manager', '财务负责人'),
        ('general_manager', '总经理'),
    ]
    
    department = models.ForeignKey(
        'Department',
        verbose_name="部门",
        on_delete=models.CASCADE,
        related_name='dept_managers'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="管理人员",
        on_delete=models.CASCADE,
        related_name='managed_depts'
    )
    role = models.CharField("角色", max_length=30, choices=ROLE_CHOICES)
    approval_level = models.IntegerField("审批级别", default=1, help_text="1=部门级，2=上级")
    is_primary = models.BooleanField("是否主要责任人", default=False, help_text="同角色中优先匹配")
    is_active = models.BooleanField("是否有效", default=True)
    
    # 时间戳
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        ordering = ['department', 'approval_level', 'is_primary']
        verbose_name = "部门主管"
        verbose_name_plural = "部门主管"
        unique_together = ['department', 'user', 'role']  # 同一用户在同一部门不能有相同角色
    
    def __str__(self):
        return f"{self.department.name} - {self.user.username} - {self.get_role_display()}"


class ApprovalFlowConfig(models.Model):
    """审批流程配置表 - 定义不同情况下的审批流程"""
    
    FLOW_TYPE_CHOICES = [
        ('contract_approval', '合同审批'),
        ('project_approval', '项目审批'),
        ('expense_approval', '费用审批'),
    ]
    
    flow_type = models.CharField("流程类型", max_length=30, choices=FLOW_TYPE_CHOICES)
    department = models.ForeignKey(
        'Department',
        verbose_name="适用部门",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="为空表示适用于所有部门"
    )
    approval_level = models.IntegerField("审批级别", default=1, help_text="1=部门级，2=上级")
    approver_role = models.CharField("审批人角色", max_length=30, choices=DepartmentManager.ROLE_CHOICES)
    priority = models.IntegerField("优先级", default=100, help_text="数字越小优先级越高")
    is_active = models.BooleanField("是否启用", default=True)
    
    # 时间戳
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        ordering = ['flow_type', 'priority', 'approval_level']
        verbose_name = "审批流程配置"
        verbose_name_plural = "审批流程配置"
        unique_together = ['flow_type', 'department', 'approval_level']
    
    def __str__(self):
        dept_name = self.department.name if self.department else "全公司"
        return f"{self.get_flow_type_display()} - {dept_name} - 第{self.approval_level}级"
