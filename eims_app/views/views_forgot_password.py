"""
忘记密码相关视图
包括：发送验证码、验证手机号、重置密码等功能
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json

from eims_app.models.model_user import UserProfile
from eims_app.models.model_sms import SMSVerificationRecord
from eims_app.sms_service import SMSService, validate_phone_number


def forgot_password_page(request):
    """忘记密码页面"""
    # 如果已登录，重定向到首页
    if request.user.is_authenticated:
        return redirect('/')
    
    return render(request, 'auth/forgot_password.html')


@require_POST
def send_forgot_password_code(request):
    """
    发送忘记密码验证码
    
    POST 参数:
        phone: 手机号码
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        
        # 验证手机号格式
        valid, message = validate_phone_number(phone)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 检查手机号是否已绑定
        try:
            UserProfile.objects.get(phone=phone)
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': '该手机号未绑定任何账号，请联系管理员'
            })
        
        # 检查发送频率（60秒内只能发送一次）
        cache_key = f'sms_forgot_{phone}'
        if cache.get(cache_key):
            return JsonResponse({
                'success': False, 
                'message': '发送过于频繁，请60秒后再试'
            })
        
        # 发送短信
        success, message = SMSService.send_sms(phone, SMSService.TYPE_RESET_PASSWORD)
        
        if success:
            # 设置发送频率限制
            cache.set(cache_key, True, 60)
            
            # 记录发送日志
            SMSVerificationRecord.objects.create(
                phone=phone,
                verification_type=SMSService.TYPE_RESET_PASSWORD,
                verification_code='***',
                status='success',
                expire_time=timezone.now() + timedelta(seconds=SMSService.CODE_EXPIRE_TIME),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            )
            return JsonResponse({'success': True, 'message': message})
        else:
            return JsonResponse({'success': False, 'message': message})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'发送失败：{str(e)}'})


@require_POST
def verify_and_reset_password(request):
    """
    验证手机号并重置密码
    
    POST 参数:
        phone: 手机号码
        code: 验证码
        new_password: 新密码
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')
        new_password = data.get('new_password')
        
        # 验证手机号
        valid, message = validate_phone_number(phone)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 验证密码强度（至少6位）
        if not new_password or len(new_password) < 6:
            return JsonResponse({
                'success': False, 
                'message': '密码长度至少6位'
            })
        
        # 验证短信验证码
        valid, message = SMSService.verify_code(phone, SMSService.TYPE_RESET_PASSWORD, code)
        if not valid:
            # 记录验证失败
            SMSVerificationRecord.objects.create(
                phone=phone,
                verification_type=SMSService.TYPE_RESET_PASSWORD,
                verification_code='***',
                status='failed',
                expire_time=timezone.now(),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                remark=f'验证码错误：{code}'
            )
            return JsonResponse({'success': False, 'message': message})
        
        # 查找用户
        try:
            profile = UserProfile.objects.get(phone=phone)
            user = profile.user
            
            if not user.is_active:
                return JsonResponse({'success': False, 'message': '账号已被禁用，请联系管理员'})
            
            # 设置新密码
            user.set_password(new_password)
            user.save()
            
            # 清除该手机号的所有验证码
            SMSService.clear_codes(phone)
            
            # 记录密码重置成功
            SMSVerificationRecord.objects.create(
                phone=phone,
                verification_type=SMSService.TYPE_RESET_PASSWORD,
                verification_code='***',
                status='success',
                expire_time=timezone.now(),
                verified_time=timezone.now(),
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                remark='密码重置成功'
            )
            
            return JsonResponse({
                'success': True,
                'message': '密码重置成功，请使用新密码登录',
                'redirect_url': '/login/'
            })
        
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '该手机号未绑定任何账号'
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'重置失败：{str(e)}'})


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
