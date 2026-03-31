from django.db import models
import os

def file_upload_path(instance, filename):
    """自定义文件上传路径：media/file_manage/日期/文件名"""
    import datetime
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    return f'file_manage/{date_str}/{filename}'

class FileManage(models.Model):
    """文件管理模块数据模型"""
    # 基础字段
    file_name = models.CharField(max_length=255, verbose_name='文件名称', help_text='请输入文件名称')
    file_path = models.FileField(upload_to=file_upload_path, verbose_name='文件路径', help_text='请选择上传文件')
    # 新增字段
    file_category = models.CharField(max_length=100, blank=True, null=True, verbose_name='文件类别', help_text='请选择文件类别')
    file_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='文件编号', help_text='请输入文件编号')
    content_summary = models.TextField(blank=True, null=True, verbose_name='内容摘要', help_text='请输入文件内容摘要')
    publish_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='发布时间')
    uploader = models.CharField(max_length=100, blank=True, null=True, verbose_name='上传人', help_text='系统自动获取')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')  # 数据库中实际是 upload_time
    remark = models.TextField(blank=True, null=True, verbose_name='备注', help_text='请输入备注信息')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    # 其他字段（自动计算/可选）
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小（字节）')
    file_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='文件类型', help_text='自动识别，无需输入')
    file_format = models.CharField(max_length=50, blank=True, null=True, verbose_name='文件格式', help_text='自动识别，只读')

    class Meta:
        verbose_name = '文件'
        verbose_name_plural = '文件管理'
        ordering = ('-publish_time',)

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        """保存文件时，自动计算文件大小、识别文件类型"""
        if self.file_path:
            # 计算文件大小（字节）
            self.file_size = self.file_path.size
            # 识别文件类型（后缀名）
            self.file_type = os.path.splitext(self.file_path.name)[1].lower()
            # 识别文件格式（大写字母，不含点）
            file_ext = os.path.splitext(self.file_path.name)[1]
            self.file_format = file_ext[1:].upper() if file_ext else ''
        # 调用父类的 save 方法真正保存到数据库
        super().save(*args, **kwargs)
