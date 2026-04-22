from django.db import models
from django.contrib.auth.models import User

class FileAccessPermission(models.Model):
    """文件访问权限模型"""
    PERMISSION_CHOICES = [
        ('view', '仅查看'),
        ('download', '查看 + 下载'),
        ('upload', '查看 + 下载 + 上传'),
        ('admin', '完全控制'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_permissions', verbose_name='用户', db_constraint=False)
    permission_type = models.CharField('权限类型', max_length=20, choices=PERMISSION_CHOICES, default='view')
    can_preview_office = models.BooleanField('可否预览 Office 文档', default=False, help_text='是否允许使用 Office Online 预览')
    can_batch_upload = models.BooleanField('可否批量上传', default=False, help_text='是否允许一次上传多个文件')
    can_manage_versions = models.BooleanField('可否管理版本', default=False, help_text='是否允许上传新版本/删除旧版本')
    
    # 适用范围
    apply_to_notices = models.BooleanField('适用于通知公告', default=True)
    apply_to_file_manage = models.BooleanField('适用于文件管理', default=True)
    
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注说明', blank=True, null=True)

    class Meta:
        verbose_name = '文件访问权限'
        verbose_name_plural = '文件访问权限'
        unique_together = ['user']

    def __str__(self):
        return f"{self.user.username} - {self.get_permission_type_display()}"


def check_file_permission(user, permission_type, module='notice'):
    """
    检查用户是否有指定权限
    
    Args:
        user: 用户对象
        permission_type: 权限类型 ('view', 'download', 'upload', 'admin')
        module: 模块名称 ('notice' 或 'file_manage')
    
    Returns:
        bool: 是否有权限
    """
    if not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    try:
        permission = FileAccessPermission.objects.get(user=user, is_deleted=False)
        
        # 检查模块适用性
        if module == 'notice' and not permission.apply_to_notices:
            return False
        elif module == 'file_manage' and not permission.apply_to_file_manage:
            return False
        
        # 权限等级检查
        permission_levels = {'view': 1, 'download': 2, 'upload': 3, 'admin': 4}
        user_level = permission_levels.get(permission.permission_type, 0)
        required_level = permission_levels.get(permission_type, 0)
        
        return user_level >= required_level
    except FileAccessPermission.DoesNotExist:
        # 默认只允许查看
        return permission_type == 'view'
