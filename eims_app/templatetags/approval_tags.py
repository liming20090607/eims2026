from django import template
from django.utils.safestring import mark_safe
from eims_app.models.model_contract_approval import ContractApproval

register = template.Library()

@register.simple_tag(takes_context=True)
def get_pending_approvals_count(context):
    """获取当前用户的待审批合同数量"""
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return 0
    
    user = request.user
    
    # 统计待审批的合同数量
    pending_count = ContractApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing']
    ).count()
    
    return pending_count


@register.inclusion_tag('widgets/pending_approval_badge.html', takes_context=True)
def render_pending_approval_badge(context):
    """渲染待审批徽章组件"""
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return {'count': 0}
    
    user = request.user
    
    # 统计待审批的合同数量
    pending_count = ContractApproval.objects.filter(
        current_approver=user,
        status__in=['pending', 'reviewing']
    ).count()
    
    return {
        'count': pending_count,
        'user': user,
    }
