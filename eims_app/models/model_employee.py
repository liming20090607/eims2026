from django.db import models
from .base import BaseModel

class Employee(BaseModel):
    """员工基本信息 - 入职登记"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True)
    
    GENDER_CHOICES = (
        (0, '男'),
        (1, '女'),
        (2, '其他'),
    )

    EDUCATION_CHOICES = (
        ('primary', '小学'),
        ('junior', '初中'),
        ('senior', '高中'),
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
    )

    ETHNIC_CHOICES = (
        ('han', '汉族'),
        ('hui', '回族'),
        ('man', '满族'),
        ('mongol', '蒙古族'),
        ('tibetan', '藏族'),
        ('uyghur', '维吾尔族'),
        ('other', '其他'),
    )

    # 唯一标识
    employee_code = models.CharField(max_length=50, unique=True, verbose_name='员工编号', help_text='请输入唯一的员工编号')
    
    # 个人基本信息
    name = models.CharField(max_length=50, verbose_name='姓名', help_text='请输入人员姓名')
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别', help_text='请选择人员性别')
    id_card = models.CharField(max_length=18, verbose_name='身份证号', help_text='18 位身份证号码')
    native_place = models.CharField(max_length=100, blank=True, verbose_name='籍贯', help_text='填写籍贯')
    ethnic = models.CharField(max_length=20, choices=ETHNIC_CHOICES, default='han', verbose_name='民族', help_text='选择民族')
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='bachelor', verbose_name='学历', help_text='选择最高学历')
    
    # 联系方式
    address = models.CharField(max_length=200, blank=True, verbose_name='住址', help_text='填写详细住址')
    home_phone = models.CharField(max_length=20, blank=True, verbose_name='固定电话', help_text='家庭固定电话')
    mobile = models.CharField(max_length=20, verbose_name='手机号', help_text='请输入手机号码')
    emergency_contact = models.CharField(max_length=50, blank=True, verbose_name='应急联系人', help_text='填写应急联系人姓名')
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name='应急电话', help_text='填写应急联系电话')
    wechat = models.CharField(max_length=50, blank=True, verbose_name='微信', help_text='填写微信号')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱', help_text='填写电子邮箱')
    
    # 职务信息
    admin_position = models.CharField(max_length=100, blank=True, verbose_name='行政职务', help_text='填写行政职务')
    tech_position = models.CharField(max_length=100, blank=True, verbose_name='技术职务', help_text='填写技术职务')
    professional_qualification = models.CharField(max_length=200, blank=True, verbose_name='执业资格', help_text='填写执业资格证书名称')
    professional_title = models.CharField(max_length=100, blank=True, verbose_name='职称', help_text='填写专业技术职称')
    job_qualification = models.CharField(max_length=200, blank=True, verbose_name='任职资格', help_text='填写任职资格')
    
    # 入职时间
    entry_time = models.DateField(null=True, blank=True, verbose_name='入职时间', help_text='选择入职时间')
    leave_time = models.DateField(null=True, blank=True, verbose_name='离职时间', help_text='选择离职时间')
    
    # 系统字段
    operator = models.CharField(max_length=100, blank=True, verbose_name='操作人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    remark = models.TextField(blank=True, default='', verbose_name='备注', help_text='可选，输入备注信息')

    class Meta:
        verbose_name = '员工信息'
        verbose_name_plural = '员工信息管理'
        ordering = ('-entry_time',)

    def __str__(self):
        return f"{self.employee_code} - {self.name}"

