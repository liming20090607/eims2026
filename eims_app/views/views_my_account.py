"""
我的账号管理视图
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from eims_app.models.model_user import UserProfile


@login_required
def my_account_view(request):
    """
    我的账号页面
    显示用户账号信息、手机号绑定状态等
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    return render(request, 'my_account.html', {
        'profile': profile
    })
