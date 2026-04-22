"""
微信扫码登录视图
实现电脑端显示二维码，手机扫码后确认登录的功能
"""
import qrcode
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from eims_app.models.model_qr_login import QRCodeLoginSession


def generate_qr_code(session_id):
    """生成二维码图片（base64格式）"""
    # 构建扫码URL
    qr_url = f"http://127.0.0.1:8000/qr-login/scan/{session_id}/"
    
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 转换为base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_str}"


def qr_login_page(request):
    """
    二维码登录页面（电脑端）
    URL: /qr-login/
    """
    # 如果已登录，直接跳转到首页
    if request.user.is_authenticated:
        return redirect('/')
    
    # 创建新的登录会话
    ip_address = request.META.get('REMOTE_ADDR', '')
    session = QRCodeLoginSession.create_session(ip_address=ip_address)
    
    # 生成二维码
    qr_code_img = generate_qr_code(str(session.session_id))
    
    context = {
        'session_id': str(session.session_id),
        'qr_code_img': qr_code_img,
        'expires_at': session.expires_at,
    }
    
    return render(request, 'auth/qr_login.html', context)


def qr_login_scan(request, session_id):
    """
    扫码确认页面（手机端）
    URL: /qr-login/scan/{session_id}/
    """
    session = get_object_or_404(QRCodeLoginSession, session_id=session_id)
    
    # 检查会话是否有效
    if not session.is_valid():
        return render(request, 'auth/qr_login_expired.html', {
            'message': '二维码已过期或无效，请重新获取'
        })
    
    # 如果用户未登录，先让用户登录
    if not request.user.is_authenticated:
        # 保存session_id到session，登录后再跳转回来
        request.session['qr_login_session_id'] = str(session_id)
        return redirect('/login/')
    
    # 用户已登录，显示确认页面
    context = {
        'session': session,
        'user': request.user,
    }
    
    return render(request, 'auth/qr_login_confirm.html', context)


def qr_login_confirm(request):
    """
    确认登录（AJAX）
    URL: /qr-login/confirm/ (POST)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '请求方法错误'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
    
    session_id = request.POST.get('session_id')
    if not session_id:
        return JsonResponse({'success': False, 'message': '缺少会话ID'}, status=400)
    
    try:
        session = QRCodeLoginSession.objects.get(session_id=session_id)
        
        # 检查会话是否有效
        if not session.is_valid():
            return JsonResponse({'success': False, 'message': '二维码已过期或无效'})
        
        # 更新会话状态
        session.status = 'confirmed'
        session.user = request.user
        session.confirmed_at = timezone.now()
        session.save()
        
        return JsonResponse({
            'success': True, 
            'message': '登录确认成功',
            'username': request.user.username,
            'real_name': getattr(request.user, 'get_full_name', lambda: request.user.username)()
        })
        
    except QRCodeLoginSession.DoesNotExist:
        return JsonResponse({'success': False, 'message': '会话不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'确认失败：{str(e)}'}, status=500)


def qr_login_status(request, session_id):
    """
    检查登录状态（AJAX轮询）
    URL: /qr-login/status/{session_id}/
    """
    try:
        session = QRCodeLoginSession.objects.get(session_id=session_id)
        
        # 检查是否过期
        if session.is_expired():
            session.status = 'expired'
            session.save()
            return JsonResponse({
                'status': 'expired',
                'message': '二维码已过期'
            })
        
        # 返回当前状态
        response_data = {
            'status': session.status,
        }
        
        # 如果已确认，返回用户信息
        if session.status == 'confirmed' and session.user:
            response_data.update({
                'username': session.user.username,
                'real_name': session.user.get_full_name() or session.user.username,
            })
        
        return JsonResponse(response_data)
        
    except QRCodeLoginSession.DoesNotExist:
        return JsonResponse({
            'status': 'invalid',
            'message': '会话不存在'
        }, status=404)


def qr_login_complete(request, session_id):
    """
    完成登录（电脑端自动跳转）
    URL: /qr-login/complete/{session_id}/
    """
    try:
        session = QRCodeLoginSession.objects.get(session_id=session_id)
        
        # 检查会话状态
        if session.status != 'confirmed':
            return render(request, 'auth/qr_login_waiting.html', {
                'message': '等待确认中...'
            })
        
        # 执行登录
        user = session.user
        if user:
            auth_login(request, user)
            
            # 清除会话
            session.delete()
            
            # 跳转到首页
            return redirect('/')
        else:
            return render(request, 'auth/qr_login_error.html', {
                'message': '登录失败，用户不存在'
            })
            
    except QRCodeLoginSession.DoesNotExist:
        return render(request, 'auth/qr_login_error.html', {
            'message': '会话不存在'
        })


def qr_login_cancel(request):
    """
    取消登录（AJAX）
    URL: /qr-login/cancel/ (POST)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '请求方法错误'}, status=405)
    
    session_id = request.POST.get('session_id')
    if not session_id:
        return JsonResponse({'success': False, 'message': '缺少会话ID'}, status=400)
    
    try:
        session = QRCodeLoginSession.objects.get(session_id=session_id)
        
        # 只有pending状态才能取消
        if session.status == 'pending':
            session.status = 'cancelled'
            session.save()
            return JsonResponse({'success': True, 'message': '已取消'})
        else:
            return JsonResponse({'success': False, 'message': '无法取消当前状态的会话'})
            
    except QRCodeLoginSession.DoesNotExist:
        return JsonResponse({'success': False, 'message': '会话不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'取消失败：{str(e)}'}, status=500)
