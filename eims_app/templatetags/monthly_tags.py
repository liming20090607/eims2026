from django import template
from datetime import date
import calendar

register = template.Library()

# 导入内置的 abs 函数，避免与自定义的 abs 过滤器冲突
_builtin_abs = abs

@register.simple_tag
def days_in_month():
    """返回当前月份的总天数"""
    today = date.today()
    return calendar.monthrange(today.year, today.month)[1]


@register.filter
def abs(value):
    """返回绝对值"""
    return _builtin_abs(int(value))
