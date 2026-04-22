from django.db import models
from .base import BaseModel

class ProjectDynamic(BaseModel):
    """项目动态模型 - 跟踪项目进度和变更"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True,
                               db_constraint=False)
    
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE, verbose_name='关联项目', help_text='选择关联的项目', null=True, blank=True)
    project_code = models.CharField(max_length=50, verbose_name='项目编号', db_index=True, blank=True, default='')
    
    project_progress = models.CharField(max_length=100, blank=True, verbose_name='项目进度', help_text='如：地基施工中/主体封顶/装修阶段')
    
    PROJECT_STATUS_CHOICES = [
        ('not_started', '未开工'),
        ('normal_construction', '正常施工'),
        ('stopped', '在停工'),
        ('completed', '已完工')
    ]
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, blank=True, verbose_name='项目状态')
    
    notice_entry = models.DateField(blank=True, null=True, verbose_name='通知进场', help_text='通知进场日期')
    delay_status = models.CharField(max_length=200, blank=True, verbose_name='延期情况', help_text='描述延期情况')
    
    planned_start_time = models.DateField(blank=True, null=True, verbose_name='计划开工时间')
    actual_start_time = models.DateField(blank=True, null=True, verbose_name='实际开工时间')
    planned_completion = models.DateField(blank=True, null=True, verbose_name='预计竣工时间')
    
    personnel_change = models.CharField(max_length=200, blank=True, verbose_name='本月人员变动', help_text='如：新增3人/离职1人')
    
    operator = models.CharField(max_length=100, blank=True, verbose_name='操作人')
    remark = models.TextField(blank=True, verbose_name='备注')
    
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '项目动态'
        verbose_name_plural = '项目动态管理'
        ordering = ('-update_time',)

    def __str__(self):
        return f"{self.project.project_name} - {self.update_time.strftime('%Y-%m-%d')}"
