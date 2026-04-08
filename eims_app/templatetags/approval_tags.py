from django import template
from django.utils.safestring import mark_safe
from eims_app.models.model_contract_approval import ContractApproval
from eims_app.models.model_seal_approval import SealApproval
from eims_app.models.model_archive_approval import ArchiveApproval

register = template.Library()

@register.simple_tag(takes_context=True)
def get_pending_approvals_count(context):
    """获取当前用户的待审批数量（合同+用印+归档）"""
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return 0
    
    user = request.user
    
    # 统计所有待审批的数量
    contract_count = ContractApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).count()
    
    seal_count = SealApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).count()
    
    archive_count = ArchiveApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).count()
    
    return contract_count + seal_count + archive_count


@register.inclusion_tag('widgets/pending_approval_badge.html', takes_context=True)
def render_pending_approval_badge(context):
    """渲染待审批徽章组件"""
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return {'count': 0}
    
    user = request.user
    
    # 统计所有待审批的数量
    contract_count = ContractApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).count()
    
    seal_count = SealApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).count()
    
    archive_count = ArchiveApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing'],
        is_deleted=False
    ).count()
    
    total_count = contract_count + seal_count + archive_count
    
    return {
        'count': total_count,
        'user': user,
    }
