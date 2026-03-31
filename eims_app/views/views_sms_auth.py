"""
短信认证相关视图
包括：发送验证码、短信登录、重置密码等功能
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json

from eims_app.models.model_user import UserProfile
from eims_app.models.model_sms import SMSVerificationRecord
from eims_app.sms_service import SMSService, validate_phone_number


@require_POST
def send_sms_code(request):
    """
    发送短信验证码 API
    
    POST 参数:
        phone: 手机号码
        code_type: 验证码类型 (login, reset_password, change_phone)
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        code_type = data.get('code_type', 'login')
        
        # 验证手机号格式
        valid, message = validate_phone_number(phone)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 检查验证码类型是否合法
        if code_type not in [SMSService.TYPE_LOGIN, SMSService.TYPE_RESET_PASSWORD, SMSService.TYPE_CHANGE_PHONE]:
            return JsonResponse({'success': False, 'message': '无效的验证码类型'})
        
        # 发送短信
        success, message = SMSService.send_sms(phone, code_type)
        
        if success:
            # 记录发送日志
            SMSVerificationRecord.objects.create(
                phone=phone,
                verification_type=code_type,
                verification_code='***',  # 不记录真实验证码
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
def sms_login(request):
    """
    短信验证码登录
    
    POST 参数:
        phone: 手机号码
        code: 验证码
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')
        
        # 验证手机号
        valid, message = validate_phone_number(phone)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 验证短信验证码
        valid, message = SMSService.verify_code(phone, SMSService.TYPE_LOGIN, code)
        if not valid:
            # 记录验证失败
            SMSVerificationRecord.objects.create(
                phone=phone,
                verification_type=SMSService.TYPE_LOGIN,
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
                return JsonResponse({'success': False, 'message': '账号已被禁用'})
            
            # 记录验证成功
            SMSVerificationRecord.objects.create(
                phone=phone,
                verification_type=SMSService.TYPE_LOGIN,
                verification_code='***',
                status='success',
                expire_time=timezone.now(),
                verified_time=timezone.now(),
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            )
            
            # 登录用户
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'redirect_url': request.GET.get('next', '/')
            })
        
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '该手机号未绑定任何账号，请先绑定手机号'
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'登录失败：{str(e)}'})


@login_required
@require_POST
def change_phone(request):
    """
    修改绑定手机号
    
    POST 参数:
        old_phone: 原手机号（可选，如果已绑定）
        new_phone: 新手机号
        code: 新手机号的验证码
    """
    try:
        data = json.loads(request.body)
        new_phone = data.get('new_phone')
        code = data.get('code')
        
        # 验证新手机号
        valid, message = validate_phone_number(new_phone)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 验证短信验证码
        valid, message = SMSService.verify_code(new_phone, SMSService.TYPE_CHANGE_PHONE, code)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 检查新手机号是否已被其他用户绑定
        existing_profile = UserProfile.objects.filter(phone=new_phone).exclude(user=request.user)
        if existing_profile.exists():
            return JsonResponse({'success': False, 'message': '该手机号已被其他账号绑定'})
        
        # 更新手机号
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.phone = new_phone
        profile.save()
        
        # 清除该手机号的所有验证码
        SMSService.clear_codes(new_phone)
        
        messages.success(request, '手机号修改成功！')
        return JsonResponse({'success': True, 'message': '手机号修改成功'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'修改失败：{str(e)}'})


@login_required
@require_POST
def reset_password_by_sms(request):
    """
    通过短信验证码重置密码
    
    POST 参数:
        phone: 手机号
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
        
        # 验证短信验证码
        valid, message = SMSService.verify_code(phone, SMSService.TYPE_RESET_PASSWORD, code)
        if not valid:
            return JsonResponse({'success': False, 'message': message})
        
        # 查找用户
        try:
            profile = UserProfile.objects.get(phone=phone)
            user = profile.user
            
            # 设置新密码
            user.set_password(new_password)
            user.save()
            
            messages.success(request, '密码重置成功！请使用新密码登录')
            return JsonResponse({
                'success': True,
                'message': '密码重置成功',
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
    """获取客户端 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
