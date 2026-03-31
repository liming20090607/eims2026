from django.db import models
from .base import BaseModel

class PersonnelCertificate(BaseModel):
    """人员证书模型"""
    
    CERTIFICATE_TYPE_CHOICES = (
        ('qualification', '职业资格证书'),
        ('training', '培训证书'),
        ('academic', '学历证书'),
        ('technical', '专业技术证书'),
        ('other', '其他证书'),
    )
    
    certificate_code = models.CharField(max_length=50, unique=True, verbose_name='证书编号', help_text='请输入证书编号')
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, verbose_name='所属人员', help_text='选择证书所属人员')
    personnel_code = models.CharField(max_length=50, verbose_name='人员编号', db_index=True)
    certificate_name = models.CharField(max_length=200, verbose_name='证书名称', help_text='填写证书全称')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPE_CHOICES, verbose_name='证书类型')
    issuing_authority = models.CharField(max_length=200, verbose_name='发证机关', help_text='填写发证机关全称')
    issue_date = models.DateField(verbose_name='发证日期', help_text='选择证书发放日期')
    valid_date = models.DateField(blank=True, null=True, verbose_name='有效期至', help_text='选择证书有效期截止日期')
    certificate_file = models.FileField(upload_to='certificates/%Y/%m/', blank=True, null=True, verbose_name='证书附件', help_text='可上传证书扫描件')
    remark = models.TextField(blank=True, null=True, verbose_name='备注', help_text='可选，输入备注信息')
    
    # 自动记录
    operator = models.CharField(max_length=100, blank=True, verbose_name='操作人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '人员证书'
        verbose_name_plural = '人员证书管理'
        ordering = ('-create_time',)
    
    def __str__(self):
        return f"{self.personnel_code} - {self.certificate_name}"


class PersonnelAllocation(BaseModel):
    """人员分配模型"""
    
    ALLOCATION_STATUS_CHOICES = (
        ('allocated', '已分配'),
        ('pending', '待分配'),
        ('recalled', '已召回'),
        ('transferred', '已调动'),
    )
    
    allocation_code = models.CharField(max_length=50, unique=True, verbose_name='分配编号', help_text='系统自动生成')
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, verbose_name='人员', help_text='选择被分配的人员')
    personnel_code = models.CharField(max_length=50, verbose_name='人员编号', db_index=True)
    from_project = models.ForeignKey('ProjectDetail', related_name='from_projects', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='原项目', help_text='选择原项目')
    from_project_code = models.CharField(max_length=50, blank=True, verbose_name='原项目编号')
    to_project = models.ForeignKey('ProjectDetail', related_name='to_projects', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分配项目', help_text='选择分配到的项目')
    to_project_code = models.CharField(max_length=50, blank=True, verbose_name='分配项目编号')
    allocation_position = models.CharField(max_length=100, verbose_name='分配岗位', help_text='填写在新项目的岗位')
    allocation_department = models.CharField(max_length=100, blank=True, verbose_name='分配部门', help_text='填写在新项目的部门')
    allocation_date = models.DateField(verbose_name='分配日期', help_text='选择分配生效日期')
    expected_duration = models.CharField(max_length=50, blank=True, verbose_name='预计工期', help_text='填写预计工作期限')
    allocation_status = models.CharField(max_length=20, choices=ALLOCATION_STATUS_CHOICES, default='allocated', verbose_name='分配状态')
    allocation_reason = models.TextField(blank=True, verbose_name='分配原因', help_text='填写分配原因说明')
    remark = models.TextField(blank=True, null=True, verbose_name='备注', help_text='可选，输入备注信息')
    
    # 自动记录
    operator = models.CharField(max_length=100, blank=True, verbose_name='操作人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '人员分配'
        verbose_name_plural = '人员分配管理'
        ordering = ('-allocation_date',)
    
    def __str__(self):
        return f"{self.personnel_code} - {self.to_project_code} ({self.allocation_position})"
