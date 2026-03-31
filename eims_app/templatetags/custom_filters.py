from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    """获取模型对象指定字段的值"""
    try:
        return getattr(obj, field_name)
    except AttributeError:
        return None