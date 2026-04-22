from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    """获取模型对象指定字段的值"""
    try:
        return getattr(obj, field_name)
    except AttributeError:
        return None

@register.filter
def multiply(value, arg):
    """乘法运算"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """除法运算"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0