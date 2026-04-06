"""
微信开放平台API服务
用于处理微信扫码登录相关功能
"""
import requests
import json
from django.conf import settings


class WechatOpenPlatformService:
    """微信开放平台服务类"""
    
    def __init__(self):
        # 从settings获取配置
        self.app_id = getattr(settings, 'WECHAT_OPEN_APP_ID', '')
        self.app_secret = getattr(settings, 'WECHAT_OPEN_APP_SECRET', '')
        self.redirect_uri = getattr(settings, 'WECHAT_OPEN_REDIRECT_URI', '')
        
        # API端点
        self.AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/qrconnect'
        self.ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        self.USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo'
    
    def get_authorize_url(self, state, scope='snsapi_login'):
        """
        生成微信授权URL
        
        Args:
            state: 随机字符串，用于防止CSRF
            scope: 应用授权作用域，网站应用目前只支持snsapi_login
            
        Returns:
            授权URL
        """
        params = {
            'appid': self.app_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
        }
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{self.AUTHORIZE_URL}?{query_string}#wechat_redirect"
    
    def get_access_token(self, code):
        """
        通过code获取access_token
        
        Args:
            code: 微信返回的授权码
            
        Returns:
            dict: 包含access_token、openid等信息
        """
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'code': code,
            'grant_type': 'authorization_code',
        }
        
        try:
            response = requests.get(self.ACCESS_TOKEN_URL, params=params, timeout=10)
            result = response.json()
            
            if 'errcode' in result:
                raise Exception(f"微信API错误: {result.get('errmsg', '未知错误')}")
            
            return {
                'success': True,
                'access_token': result.get('access_token'),
                'refresh_token': result.get('refresh_token'),
                'openid': result.get('openid'),
                'unionid': result.get('unionid', ''),
                'expires_in': result.get('expires_in', 7200),
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_info(self, access_token, openid):
        """
        获取用户信息
        
        Args:
            access_token: 接口调用凭证
            openid: 用户唯一标识
            
        Returns:
            dict: 用户信息
        """
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN',
        }
        
        try:
            response = requests.get(self.USERINFO_URL, params=params, timeout=10)
            result = response.json()
            
            if 'errcode' in result:
                raise Exception(f"微信API错误: {result.get('errmsg', '未知错误')}")
            
            return {
                'success': True,
                'openid': result.get('openid'),
                'unionid': result.get('unionid', ''),
                'nickname': result.get('nickname', ''),
                'headimgurl': result.get('headimgurl', ''),
                'sex': result.get('sex', 0),
                'country': result.get('country', ''),
                'province': result.get('province', ''),
                'city': result.get('city', ''),
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def refresh_access_token(self, refresh_token):
        """
        刷新access_token
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            dict: 新的access_token信息
        """
        params = {
            'appid': self.app_id,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        
        try:
            response = requests.get(self.ACCESS_TOKEN_URL, params=params, timeout=10)
            result = response.json()
            
            if 'errcode' in result:
                raise Exception(f"微信API错误: {result.get('errmsg', '未知错误')}")
            
            return {
                'success': True,
                'access_token': result.get('access_token'),
                'refresh_token': result.get('refresh_token'),
                'openid': result.get('openid'),
                'expires_in': result.get('expires_in', 7200),
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_configured(self):
        """检查是否已配置微信开放平台"""
        return bool(self.app_id and self.app_secret and self.redirect_uri)


# 创建全局实例
wechat_service = WechatOpenPlatformService()
