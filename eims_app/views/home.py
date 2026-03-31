# eims_app/views/home.py
from django.shortcuts import render

def home_view(request):
    """首页视图"""
    return render(request, 'home.html')  # 稍后创建此模板