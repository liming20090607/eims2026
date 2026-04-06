"""
微信扫码登录视图（真正的微信开放平台集成）
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from eims_app.models.model_wechat_binding import WechatUserBinding, WechatQRCodeSession
from eims_app.services.wechat_service import wechat_service


def wechat_qr_login_page(request):
    """
    微信扫码登录页面（电脑端）
    URL: /wechat-login/
    """
    # 如果已登录，直接跳转到首页
    if request.user.is_authenticated:
        return redirect('/')
    
    # 检查微信配置
    if not wechat_service.is_configured():
        return render(request, 'auth/wechat_login_config_error.html', {
            'message': '微信开放平台未配置，请联系管理员'
        })
    
    # 创建新的扫码会话
    ip_address = request.META.get('REMOTE_ADDR', '')
    session = WechatQRCodeSession.create_session(ip_address=ip_address)
    
    # 生成微信授权URL
    authorize_url = wechat_service.get_authorize_url(state=session.state)
    
    context = {
        'session_id': str(session.session_id),
        'state': session.state,
        'authorize_url': authorize_url,
        'app_id': wechat_service.app_id,
        'redirect_uri': wechat_service.redirect_uri,
    }
    
    return render(request, 'auth/wechat_qr_login.html', context)


def wechat_login_callback(request):
    """
    微信授权回调（处理微信返回的code）
    URL: /wechat-login/callback/
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code or not state:
        return render(request, 'auth/wechat_login_error.html', {
            'message': '授权参数不完整'
        })
    
    # 验证会话
    try:
        session = WechatQRCodeSession.objects.get(state=state)
    except WechatQRCodeSession.DoesNotExist:
        return render(request, 'auth/wechat_login_error.html', {
            'message': '会话不存在或已过期'
        })
    
    # 检查会话是否有效
    if not session.is_valid():
        return render(request, 'auth/wechat_login_error.html', {
            'message': '二维码已过期或无效'
        })
    
    # 通过code获取access_token和openid
    token_result = wechat_service.get_access_token(code)
    
    if not token_result['success']:
        return render(request, 'auth/wechat_login_error.html', {
            'message': f'获取授权信息失败：{token_result.get("error")}'
        })
    
    openid = token_result['openid']
    unionid = token_result.get('unionid', '')
    
    # 更新会话状态
    session.status = 'authorized'
    session.code = code
    session.openid = openid
    session.unionid = unionid
    session.authorized_at = timezone.now()
    session.save()
    
    # 尝试查找已绑定的用户
    user = WechatUserBinding.get_user_by_openid(openid)
    
    if user:
        # 用户已绑定，直接登录
        auth_login(request, user)
        
        # 更新最后登录时间
        binding = WechatUserBinding.objects.get(openid=openid)
        binding.last_login_time = timezone.now()
        binding.save()
        
        # 更新会话
        session.user = user
        session.status = 'bound'
        session.save()
        
        # 跳转到首页
        return redirect('/')
    else:
        # 用户未绑定，显示绑定页面
        # 先获取用户信息
        userinfo_result = wechat_service.get_user_info(
            token_result['access_token'], 
            openid
        )
        
        if userinfo_result['success']:
            # 保存用户信息到session，供后续绑定使用
            request.session['wechat_temp_userinfo'] = userinfo_result
            request.session['wechat_temp_openid'] = openid
            request.session['wechat_temp_unionid'] = unionid
            request.session['wechat_session_id'] = str(session.session_id)
        
        return render(request, 'auth/wechat_bind_account.html', {
            'openid': openid,
            'nickname': userinfo_result.get('nickname', '微信用户') if userinfo_result['success'] else '微信用户',
            'headimgurl': userinfo_result.get('headimgurl', '') if userinfo_result['success'] else '',
        })


def wechat_bind_account(request):
    """
    绑定微信账号页面
    URL: /wechat-login/bind/
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 从session获取临时信息
        openid = request.session.get('wechat_temp_openid')
        unionid = request.session.get('wechat_temp_unionid', '')
        session_id = request.session.get('wechat_session_id')
        
        if not openid:
            return JsonResponse({
                'success': False,
                'message': '会话信息丢失，请重新扫码'
            })
        
        # 验证用户凭据
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return JsonResponse({
                'success': False,
                'message': '用户名或密码错误'
            })
        
        # 检查该微信是否已绑定其他账号
        existing_binding = WechatUserBinding.objects.filter(openid=openid).first()
        if existing_binding and existing_binding.user != user:
            return JsonResponse({
                'success': False,
                'message': '该微信已绑定其他账号'
            })
        
        # 绑定微信
        userinfo = request.session.get('wechat_temp_userinfo', {})
        binding, created = WechatUserBinding.bind_user(
            user=user,
            openid=openid,
            unionid=unionid,
            nickname=userinfo.get('nickname', ''),
            headimgurl=userinfo.get('headimgurl', ''),
            sex=userinfo.get('sex', 0),
            country=userinfo.get('country', ''),
            province=userinfo.get('province', ''),
            city=userinfo.get('city', ''),
        )
        
        # 自动登录
        auth_login(request, user)
        
        # 更新会话
        if session_id:
            try:
                session = WechatQRCodeSession.objects.get(session_id=session_id)
                session.user = user
                session.status = 'bound'
                session.save()
            except WechatQRCodeSession.DoesNotExist:
                pass
        
        # 清除session
        if 'wechat_temp_userinfo' in request.session:
            del request.session['wechat_temp_userinfo']
        if 'wechat_temp_openid' in request.session:
            del request.session['wechat_temp_openid']
        if 'wechat_temp_unionid' in request.session:
            del request.session['wechat_temp_unionid']
        if 'wechat_session_id' in request.session:
            del request.session['wechat_session_id']
        
        return JsonResponse({
            'success': True,
            'message': '绑定成功',
            'redirect_url': '/'
        })
    
    # GET请求，显示绑定页面
    openid = request.session.get('wechat_temp_openid')
    if not openid:
        return redirect('/wechat-login/')
    
    userinfo = request.session.get('wechat_temp_userinfo', {})
    
    return render(request, 'auth/wechat_bind_account.html', {
        'openid': openid,
        'nickname': userinfo.get('nickname', '微信用户'),
        'headimgurl': userinfo.get('headimgurl', ''),
    })


def wechat_check_status(request, session_id):
    """
    检查微信扫码登录状态（AJAX轮询）
    URL: /wechat-login/status/{session_id}/
    """
    try:
        session = WechatQRCodeSession.objects.get(session_id=session_id)
        
        # 检查是否过期
        if session.is_expired():
            session.status = 'expired'
            session.save()
            return JsonResponse({
                'status': 'expired',
                'message': '二维码已过期'
            })
        
        response_data = {
            'status': session.status,
        }
        
        # 如果已绑定，返回用户信息
        if session.status == 'bound' and session.user:
            response_data.update({
                'username': session.user.username,
                'real_name': session.user.get_full_name() or session.user.username,
            })
        
        return JsonResponse(response_data)
        
    except WechatQRCodeSession.DoesNotExist:
        return JsonResponse({
            'status': 'invalid',
            'message': '会话不存在'
        }, status=404)


def wechat_unbind(request):
    """
    解绑微信（需要登录）
    URL: /wechat-login/unbind/ (POST)
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '请求方法错误'}, status=405)
    
    openid = request.POST.get('openid')
    
    try:
        binding = WechatUserBinding.objects.get(
            user=request.user,
            openid=openid,
            is_bound=True
        )
        binding.is_bound = False
        binding.save()
        
        return JsonResponse({'success': True, 'message': '解绑成功'})
    except WechatUserBinding.DoesNotExist:
        return JsonResponse({'success': False, 'message': '绑定关系不存在'}, status=404)


def wechat_my_bindings(request):
    """
    查看我的微信绑定（需要登录）
    URL: /wechat-login/my-bindings/
    """
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    bindings = WechatUserBinding.objects.filter(
        user=request.user,
        is_bound=True
    ).order_by('-bind_time')
    
    return render(request, 'auth/wechat_my_bindings.html', {
        'bindings': bindings
    })
