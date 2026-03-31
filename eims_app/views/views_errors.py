from django.shortcuts import render
from django.views.defaults import page_not_found, server_error

def custom_404(request, exception=None):
    """自定义404错误页面"""
    return page_not_found(request, exception, template_name='errors/404.html')

def custom_500(request):
    """自定义500错误页面"""
    return server_error(request, template_name='errors/500.html')

# eims_app/views/views_errors.py
import logging
logger = logging.getLogger('eims_errors')

def custom_500(request):
    logger.error(f"500 error at {request.path}: {request.META.get('ERROR_MESSAGE', 'No details')}")
    return server_error(request, template_name='errors/500.html')