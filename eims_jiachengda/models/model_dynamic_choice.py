from django.db import models
from django.contrib.auth.models import User


class DynamicChoice(models.Model):
    """动态选项表 - 用于存储各模块的 Choice 选项"""
    
    # 选项类别（使用模型名。字段名的格式）
    CATEGORY_CHOICES = [
        # 项目台账模块
        ('project.project_status', '项目状态'),
        ('project.contract_category', '合同类别'),
        ('projectdetail.project_status', '项目状态（详情）'),
        ('projectdetail.contract_category', '合同类别（详情）'),
        ('projectdetail.contract_status', '合同状态'),
        ('projectdetail.settlement_status', '结算情况'),
        ('projectdetail.construction_permit_status', '报建情况'),
        ('projectdetail.entry_notice', '进场通知'),
        
        # 项目动态模块
        ('projectdynamic.project_status', '项目动态状态'),
        
        # 人员管理模块
        ('userprofile.gender', '性别'),
        ('personnel.gender', '人员性别'),
        ('employeecertificate.certificate_type', '证书类型'),
        ('employeeallocation.allocation_status', '分配状态'),
        
        # 审批流程模块
        ('contractapproval.status', '审批状态'),
        ('contractapproval.approval_flow_type', '审批流程类型'),
        ('contractapproval.approval_result', '审批结果'),
        ('approvalattachment.file_type', '附件类型'),
        ('approvalrecord.action', '审批操作'),
        ('departmentmanager.role', '部门角色'),
        ('approvalflowconfig.flow_type', '流程类型'),
        
        # 工作流模块
        ('workflowrole.name', '工作流角色'),
        ('approvalflow.status', '工作流状态'),
        ('flowaction.action', '工作流操作'),
        
        # 用户模块
        ('userprofile.report_period', '填报周期'),
        ('monthlyreport.status', '填报状态'),
    ]
    
    category = models.CharField(
        max_length=100, 
        choices=CATEGORY_CHOICES, 
        verbose_name='选项类别',
        help_text='选择该选项所属的业务类别'
    )
    code = models.CharField(
        max_length=50, 
        verbose_name='选项代码',
        help_text='英文代码，如：not_started'
    )
    name = models.CharField(
        max_length=100, 
        verbose_name='选项名称',
        help_text='中文名称，如：未开工'
    )
    order = models.IntegerField(
        default=0, 
        verbose_name='排序',
        help_text='数字越小越靠前'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='是否启用',
        help_text='禁用后的选项将不在下拉列表中显示'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='创建人'
    )
    
    class Meta:
        verbose_name = '动态选项'
        verbose_name_plural = '动态选项管理'
        ordering = ['category', 'order', 'code']
        unique_together = ['category', 'code']  # 同一类别下代码不能重复
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"
    
    @classmethod
    def get_choices_for_category(cls, category_code):
        """获取某个类别的所有可用选项"""
        queryset = cls.objects.filter(category=category_code, is_active=True)
        return [(obj.code, obj.name) for obj in queryset]
    
    @classmethod
    def add_choice(cls, category, code, name, order=None, user=None):
        """添加新选项的便捷方法"""
        if order is None:
            # 自动设置排序为最后一个
            last_choice = cls.objects.filter(category=category).order_by('-order').first()
            order = (last_choice.order + 1) if last_choice else 0
        
        choice = cls.objects.create(
            category=category,
            code=code.lower().strip(),
            name=name.strip(),
            order=order,
            created_by=user
        )
        return choice
