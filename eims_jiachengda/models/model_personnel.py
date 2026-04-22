from django.db import models
from .base import BaseModel

class Personnel(BaseModel):
    """项目人员信息 - 二次分配"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    # 与员工基本信息关联
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True, verbose_name='员工', help_text='选择员工', related_name='project_assignments')
    
    # 项目人员基本信息（简化）
    personnel_code = models.CharField(max_length=50, verbose_name='人员编号', db_index=True, default='')
    name = models.CharField(max_length=50, verbose_name='姓名', help_text='请输入人员姓名', default='')
    gender = models.SmallIntegerField(choices=[(0, '男'), (1, '女'), (2, '其他')], default=0, verbose_name='性别')
    
    # 项目分配信息 - 支持一人多项目（最多 5 个项目）
    # project 字段作为"当前主要项目"（可选），支持一人多项目时显示主要归属
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, null=True, blank=True, verbose_name='主要项目', help_text='选择当前主要归属项目（可选）', related_name='main_personnel')
    project_code = models.CharField(max_length=50, verbose_name='项目编号', db_index=True, blank=True, default='')
    
    # 额外项目字段（支持一人多项目，最多 5 个）
    project2 = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, null=True, blank=True, verbose_name='项目 2', help_text='选择第二个项目（可选）', related_name='personnel_project2')
    project_code2 = models.CharField(max_length=50, verbose_name='项目 2 编号', db_index=True, blank=True, default='')
    
    project3 = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, null=True, blank=True, verbose_name='项目 3', help_text='选择第三个项目（可选）', related_name='personnel_project3')
    project_code3 = models.CharField(max_length=50, verbose_name='项目 3 编号', db_index=True, blank=True, default='')
    
    project4 = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, null=True, blank=True, verbose_name='项目 4', help_text='选择第四个项目（可选）', related_name='personnel_project4')
    project_code4 = models.CharField(max_length=50, verbose_name='项目 4 编号', db_index=True, blank=True, default='')
    
    project5 = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, null=True, blank=True, verbose_name='项目 5', help_text='选择第五个项目（可选）', related_name='personnel_project5')
    project_code5 = models.CharField(max_length=50, verbose_name='项目 5 编号', db_index=True, blank=True, default='')
    
    # 部门分配信息 - 一个人只能属于一个部门
    department = models.CharField(max_length=100, verbose_name='部门', help_text='请输入所属部门', default='', db_index=True)
    position = models.CharField(max_length=100, blank=True, verbose_name='岗位', help_text='请输入人员岗位', default='')
    
    # 联系方式（仅保留项目相关）
    phone = models.CharField(max_length=20, verbose_name='手机号码', help_text='请输入手机号码', default='')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱', help_text='可选，输入人员邮箱')
    
    # 时间信息
    entry_time = models.DateField(null=True, blank=True, verbose_name='入岗时间', help_text='选择入岗时间')
    leave_time = models.DateField(null=True, blank=True, verbose_name='离岗时间', help_text='选择离岗时间')
    
    # 系统字段
    operator = models.CharField(max_length=100, blank=True, verbose_name='操作人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    remark = models.TextField(blank=True, null=True, default='', verbose_name='备注', help_text='可选，输入备注信息')

    class Meta:
        verbose_name = '项目人员'
        verbose_name_plural = '项目人员管理'
        ordering = ('-create_time',)

    def __str__(self):
        project_name = self.project.project_name if self.project else '未分配'
        return f"{self.personnel_code} - {self.name} ({project_name})"
