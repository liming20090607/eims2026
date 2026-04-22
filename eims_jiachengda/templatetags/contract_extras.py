from django import template

register = template.Library()

@register.filter
def status_badge_color(status):
    """将合同状态转换为Bootstrap颜色类"""
    color_map = {
        'draft': 'secondary',      # 草稿
        'signed': 'info',          # 已签订
        'executing': 'success',    # 履行中
        'completed': 'primary',    # 已完成
        'terminated': 'danger',    # 已终止
    }
    return color_map.get(status, 'light')