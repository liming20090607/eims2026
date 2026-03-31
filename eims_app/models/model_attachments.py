from django.db import models
from django.utils import timezone
import os

class NoticeAttachment(models.Model):
    """通知公告附件模型（支持多附件）"""
    notice = models.ForeignKey('Notice', on_delete=models.CASCADE, related_name='attachments', verbose_name='通知')
    file = models.FileField('文件', upload_to='notices/attachments/')
    file_name = models.CharField('文件名称', max_length=255)
    file_size = models.BigIntegerField('文件大小（字节）', default=0)
    file_type = models.CharField('文件类型', max_length=50)
    version = models.IntegerField('版本号', default=1, help_text='文件版本号，从 1 开始')
    is_latest = models.BooleanField('是否最新版本', default=True)
    upload_person = models.CharField('上传人', max_length=100, blank=True, null=True)
    upload_time = models.DateTimeField('上传时间', auto_now_add=True)
    remark = models.TextField('备注说明', blank=True, null=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        verbose_name = '通知附件'
        verbose_name_plural = '通知附件'
        ordering = ['-version']
        indexes = [
            models.Index(fields=['notice', '-version']),
            models.Index(fields=['notice', 'is_latest']),
        ]

    def __str__(self):
        return f"{self.file_name} (v{self.version})"

    def save(self, *args, **kwargs):
        """保存时自动识别文件信息"""
        if self.file:
            # 使用 Django 的 name 属性获取文件名
            import os
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file_name)[1].lower()
        super().save(*args, **kwargs)


class FileManageVersion(models.Model):
    """文件管理版本模型（支持版本控制）"""
    file_manage = models.ForeignKey('FileManage', on_delete=models.CASCADE, related_name='versions', verbose_name='文件')
    file = models.FileField('文件', upload_to='file_manage/versions/')
    file_name = models.CharField('文件名称', max_length=255)
    file_size = models.BigIntegerField('文件大小（字节）', default=0)
    file_type = models.CharField('文件类型', max_length=50)
    version = models.IntegerField('版本号', default=1, help_text='文件版本号，从 1 开始')
    is_latest = models.BooleanField('是否最新版本', default=True)
    uploader = models.CharField('上传人', max_length=100, blank=True, null=True)
    upload_time = models.DateTimeField('上传时间', auto_now_add=True)
    change_log = models.TextField('变更说明', blank=True, null=True, help_text='本次更新的变更说明')
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        verbose_name = '文件版本'
        verbose_name_plural = '文件版本'
        ordering = ['-version']
        indexes = [
            models.Index(fields=['file_manage', '-version']),
            models.Index(fields=['file_manage', 'is_latest']),
        ]

    def __str__(self):
        return f"{self.file_name} (v{self.version})"

    def save(self, *args, **kwargs):
        """保存时自动识别文件信息"""
        if self.file:
            self.file_name = self.file.name.split('/')[-1]
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file_name)[1].lower()
        super().save(*args, **kwargs)
