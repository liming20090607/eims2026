from django import template
from django.forms.widgets import Widget

register = template.Library()

@register.filter
def add_class(field, css_class):
    """为表单字段添加CSS类"""
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    return field