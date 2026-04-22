from django import template
from eims_app.models import NoticeAttachment

register = template.Library()

@register.simple_tag
def get_notice_attachments(notice_id):
    """获取指定通知的所有附件列表"""
    return NoticeAttachment.objects.filter(
        notice_id=notice_id,
        is_deleted=False
    ).order_by('-upload_time')
