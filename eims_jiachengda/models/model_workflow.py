from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    """角色定义 - 系统角色"""
    
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('system_admin', '系统管理员'),
        ('project_director', '项目总监'),
        ('director_rep', '总监代表'),
        ('supervisor', '监理员'),
        ('data_clerk', '资料员'),
        ('initiator', '发起人'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name='角色名称')
    description = models.TextField(verbose_name='角色描述', blank=True)
    permissions = models.TextField(verbose_name='权限列表', blank=True, help_text='逗号分隔的权限代码')
    
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色管理'
    
    def __str__(self):
        return self.get_role_display()


class ProjectRole(models.Model):
    """项目角色关联 - 用户在特定项目中的角色"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', db_constraint=False)
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, verbose_name='项目')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '项目角色'
        verbose_name_plural = '项目角色管理'
        unique_together = ['user', 'project', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.project_name} - {self.role.name}"


class ApprovalFlow(models.Model):
    """审批流程定义"""
    
    FLOW_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending_review', '待总监审核'),
        ('pending_approval', '待管理员审批'),
        ('approved', '已批准'),
        ('rejected', '已退回'),
        ('cancelled', '已取消'),
    ]
    
    report = models.OneToOneField('MonthlyReport', on_delete=models.CASCADE, verbose_name='关联报告')
    current_step = models.IntegerField(default=1, verbose_name='当前步骤')
    status = models.CharField(max_length=20, choices=FLOW_STATUS_CHOICES, default='draft', verbose_name='流程状态')
    
    # 发起人
    initiator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='initiated_flows', verbose_name='发起人', db_constraint=False)
    initiate_time = models.DateTimeField(auto_now_add=True, verbose_name='发起时间')
    
    # 总监审核
    director = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='director_reviews', verbose_name='项目总监', db_constraint=False)
    director_review_time = models.DateTimeField(null=True, blank=True, verbose_name='总监审核时间')
    director_opinion = models.TextField(blank=True, verbose_name='总监意见')
    director_passed = models.BooleanField(null=True, blank=True, verbose_name='总监审核是否通过')
    
    # 管理员审批
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='admin_approvals', verbose_name='审批管理员', db_constraint=False)
    approval_time = models.DateTimeField(null=True, blank=True, verbose_name='管理员审批时间')
    approval_opinion = models.TextField(blank=True, verbose_name='审批意见')
    approval_passed = models.BooleanField(null=True, blank=True, verbose_name='管理员审批是否通过')
    
    class Meta:
        verbose_name = '审批流程'
        verbose_name_plural = '审批流程管理'
    
    def __str__(self):
        return f"{self.report.project.project_name} - {self.report} - {self.get_status_display()}"


class ApprovalRecord(models.Model):
    """审批记录 - 记录每次操作"""
    
    ACTION_CHOICES = [
        ('submit', '提交'),
        ('review_pass', '审核通过'),
        ('review_reject', '审核退回'),
        ('approve_pass', '审批通过'),
        ('approve_reject', '审批退回'),
        ('cancel', '取消'),
    ]
    
    flow = models.ForeignKey(ApprovalFlow, on_delete=models.CASCADE, verbose_name='审批流程')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人', db_constraint=False)
    opinion = models.TextField(blank=True, verbose_name='意见')
    action_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '审批记录'
        verbose_name_plural = '审批记录管理'
        ordering = ['-action_time']
    
    def __str__(self):
        return f"{self.flow.report.project.project_name} - {self.get_action_display()} - {self.operator.username}"
