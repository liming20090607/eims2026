"""
动态URL命名空间模板标签
用于在多租户系统中动态生成带命名空间的URL
"""
from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def tenant_url(context, url_name, *args, **kwargs):
    """
    根据当前租户动态生成URL
    
    用法:
    {% load tenant_tags %}
    <a href="{% tenant_url 'project_ledger_list' %}">项目台账</a>
    <a href="{% tenant_url 'employee_detail' employee.pk %}">详情</a>
    """
    # 从context中获取当前URL命名空间
    url_namespace = context.get('url_namespace', 'dingce')
    
    # 构建完整的URL名称（带命名空间）
    full_url_name = f"{url_namespace}:{url_name}"
    
    try:
        # 尝试反转URL
        return reverse(full_url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        # 如果失败，尝试不带命名空间
        try:
            return reverse(url_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            # 如果还是失败，返回#
            return '#'


@register.simple_tag(takes_context=True)
def get_url_namespace(context):
    """
    获取当前URL命名空间
    
    用法:
    {% load tenant_tags %}
    {% get_url_namespace as namespace %}
    """
    return context.get('url_namespace', 'dingce')
