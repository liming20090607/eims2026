from django.db import models

class Notice(models.Model):
    """通知公告模型（优化版 - 含关键字、批量上传）"""
    
    # ===== 租户字段（多租户数据隔离）=====
    tenant = models.ForeignKey('Tenant', on_delete=models.PROTECT, 
                               null=True, blank=True, 
                               verbose_name='所属公司',
                               help_text='数据隔离依据',
                               db_index=True)
    
    # 基础信息
    notice_code = models.CharField('公告编号', max_length=50, blank=True, null=True)
    notice_title = models.CharField('公告标题', max_length=200, blank=False, null=False, help_text='必填：通知的标题')
    keywords = models.CharField('关键字', max_length=200, blank=True, null=True, help_text='必填：用逗号或空格分隔的关键字')
    notice_type = models.CharField('公告类型', max_length=50, blank=True, null=True)  # 通知/公告/预警/提醒
    notice_scope = models.CharField('发布范围', max_length=200, blank=True, null=True)  # 全员/部门/指定人员
    
    # 内容与附件
    notice_content = models.TextField('公告内容', blank=True, null=True)
    attach_file = models.FileField('附件', upload_to='notices/', blank=True, null=True)
    file_name = models.CharField('文件名称', max_length=255, blank=True, null=True, help_text='上传文件的原始名称')
    file_size = models.BigIntegerField('文件大小（字节）', default=0, blank=True, null=True)
    file_type = models.CharField('文件类型', max_length=50, blank=True, null=True, help_text='自动识别文件后缀')
    
    # 发布信息
    publish_person = models.CharField('发布人', max_length=50, blank=True, null=True)
    effective_date = models.DateField('生效日期', blank=True, null=True)
    invalid_date = models.DateField('失效日期', blank=True, null=True)
    
    # 状态字段
    notice_status = models.CharField('公告状态', max_length=20, blank=True, null=True)  # 草稿/已发布/已撤回/已过期
    read_count = models.IntegerField('阅读次数', default=0, blank=True, null=True)
    
    # 备注与系统字段
    remark = models.TextField('备注说明', blank=True, null=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True, help_text='通知公告的创建时间（第一次发布时间）')
    update_time = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        verbose_name = '通知公告'
        verbose_name_plural = '通知公告'
        ordering = ['-create_time']

    def __str__(self):
        return self.notice_title or f'公告-{self.id}'
    
    def save(self, *args, **kwargs):
        """保存时自动识别附件信息"""
        if self.attach_file:
            self.file_name = self.attach_file.name.split('/')[-1]
            self.file_size = self.attach_file.size
            import os
            self.file_type = os.path.splitext(self.file_name)[1].lower()
        super().save(*args, **kwargs) 
