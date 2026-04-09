from django.db import models
from .base import BaseModel
from django.contrib.auth.models import User


class Department(BaseModel):
    """公司部门管理"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True)
    
    DEPARTMENT_TYPE_CHOICES = [
        ('functional', '职能部门'),
        ('project', '项目部门'),
        ('temporary', '临时部门'),
    ]
    
    STATUS_CHOICES = [
        ('active', '正常'),
        ('inactive', '停用'),
        ('merging', '合并中'),
    ]
    
    # 部门基本信息
    department_code = models.CharField(max_length=50, unique=True, verbose_name='部门编号', help_text='唯一部门标识')
    department_name = models.CharField(max_length=100, verbose_name='部门名称', help_text='部门全称')
    department_type = models.CharField(max_length=20, choices=DEPARTMENT_TYPE_CHOICES, default='functional', verbose_name='部门类型')
    parent_department = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='上级部门', related_name='child_departments')
    
    # 部门管理信息
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='部门负责人', related_name='managed_departments')
    manager_name = models.CharField(max_length=50, blank=True, verbose_name='负责人姓名', help_text='部门经理/主任姓名')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话', help_text='部门负责人联系方式')
    contact_email = models.EmailField(blank=True, verbose_name='联系邮箱', help_text='部门工作邮箱')
    
    # 部门职能描述
    description = models.TextField(blank=True, verbose_name='部门描述', help_text='部门主要职责和工作范围')
    responsibilities = models.TextField(blank=True, verbose_name='部门职能', help_text='详细职能说明')
    
    # 部门状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='部门状态')
    established_date = models.DateField(blank=True, null=True, verbose_name='成立日期')
    
    # 排序和显示
    order = models.IntegerField(default=0, verbose_name='排序顺序', help_text='数字越小越靠前')
    
    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        ordering = ['order', 'department_code']
        indexes = [
            models.Index(fields=['department_code']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.department_code} - {self.department_name}"
    
    @property
    def full_path(self):
        """获取完整部门路径（包含上级部门）"""
        if self.parent_department:
            return f"{self.parent_department.full_path} > {self.department_name}"
        return self.department_name
    
    @property
    def member_count(self):
        """部门人数统计"""
        from eims_app.models.model_personnel import Personnel
        return Personnel.objects.filter(department=self.department_name, is_deleted=False).count()


class DepartmentRole(BaseModel):
    """部门内角色配置"""
    
    ROLE_TYPE_CHOICES = [
        ('manager', '部门经理'),
        ('deputy', '部门副职'),
        ('supervisor', '主管'),
        ('member', '普通成员'),
        ('assistant', '助理'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门', related_name='department_roles')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='department_roles')
    role_type = models.CharField(max_length=20, choices=ROLE_TYPE_CHOICES, verbose_name='角色类型')
    role_name = models.CharField(max_length=50, verbose_name='角色名称', help_text='如：工程部经理、技术部主管等')
    is_primary = models.BooleanField(default=False, verbose_name='是否主要负责人', help_text='同一角色类型只能有一个主要负责人')
    permissions = models.TextField(blank=True, verbose_name='权限列表', help_text='逗号分隔的权限代码')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='直属上级', related_name='supervised_employees')
    
    class Meta:
        verbose_name = '部门角色'
        verbose_name_plural = '部门角色配置'
        unique_together = ['department', 'user', 'role_type']
        indexes = [
            models.Index(fields=['department', 'role_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.department.department_name} - {self.role_name}"


class ApprovalChain(BaseModel):
    """审批链条配置 - 支持多级审批"""
    
    CHAIN_TYPE_CHOICES = [
        ('sequential', '逐级审批'),
        ('parallel', '并行审批'),
        ('hybrid', '混合审批'),
    ]
    
    BUSINESS_TYPE_CHOICES = [
        ('personnel_allocate', '人员分配'),
        ('personnel_transfer', '人员调动'),
        ('leave_apply', '请假申请'),
        ('expense_apply', '费用报销'),
        ('contract_sign', '合同签订'),
        ('payment_apply', '付款申请'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='审批链名称', help_text='如：人员分配审批流程')
    business_type = models.CharField(max_length=30, choices=BUSINESS_TYPE_CHOICES, verbose_name='业务类型')
    chain_type = models.CharField(max_length=20, choices=CHAIN_TYPE_CHOICES, default='sequential', verbose_name='审批类型')
    description = models.TextField(blank=True, verbose_name='审批链描述')
    
    # 审批级别配置
    level_1_department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='一级审批部门', related_name='level_1_approvals')
    level_1_role = models.CharField(max_length=50, verbose_name='一级审批角色', help_text='如：部门经理')
    
    level_2_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='二级审批部门', related_name='level_2_approvals')
    level_2_role = models.CharField(max_length=50, blank=True, verbose_name='二级审批角色')
    
    level_3_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='三级审批部门', related_name='level_3_approvals')
    level_3_role = models.CharField(max_length=50, blank=True, verbose_name='三级审批角色')
    
    # 是否需要跨部门协同
    need_cross_department = models.BooleanField(default=False, verbose_name='是否需要跨部门协同')
    cross_departments = models.ManyToManyField(Department, blank=True, verbose_name='协同部门', related_name='cross_dept_approvals')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        verbose_name = '审批链配置'
        verbose_name_plural = '审批链管理'
        ordering = ['business_type', 'name']
    
    def __str__(self):
        return f"{self.get_business_type_display()} - {self.name}"
    
    def get_approval_levels(self):
        """获取所有审批级别"""
        levels = []
        if self.level_1_department:
            levels.append({
                'level': 1,
                'department': self.level_1_department,
                'role': self.level_1_role
            })
        if self.level_2_department:
            levels.append({
                'level': 2,
                'department': self.level_2_department,
                'role': self.level_2_role
            })
        if self.level_3_department:
            levels.append({
                'level': 3,
                'department': self.level_3_department,
                'role': self.level_3_role
            })
        return levels
