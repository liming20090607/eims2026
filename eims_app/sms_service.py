"""
短信服务工具模块
提供短信验证码发送和验证功能
"""
import random
import time
from django.core.cache import cache
from django.conf import settings


class SMSService:
    """
    短信服务类
    
    注意：这是一个示例实现，实际使用时需要替换为真实的短信服务商 API
    推荐的短信服务商：
    - 阿里云短信
    - 腾讯云短信
    - 华为云短信
    - 容联云通讯
    """
    
    # 验证码类型
    TYPE_LOGIN = 'login'  # 登录验证码
    TYPE_RESET_PASSWORD = 'reset_password'  # 重置密码验证码
    TYPE_CHANGE_PHONE = 'change_phone'  # 修改手机号验证码
    
    # 验证码有效期（秒）
    CODE_EXPIRE_TIME = 300  # 5 分钟
    
    # 发送频率限制（秒）
    SEND_INTERVAL = 60  # 60 秒内只能发送一次
    
    # 每日发送次数限制
    DAILY_LIMIT = 10  # 每个手机号每天最多 10 次
    
    @classmethod
    def generate_code(cls, length=6):
        """生成指定位数的数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    @classmethod
    def _get_cache_key(cls, phone, code_type):
        """生成缓存键"""
        return f'sms_code_{code_type}_{phone}'
    
    @classmethod
    def _get_send_time_key(cls, phone):
        """获取发送时间缓存键"""
        return f'sms_send_time_{phone}'
    
    @classmethod
    def _get_daily_count_key(cls, phone):
        """获取每日发送次数缓存键"""
        date_str = time.strftime('%Y%m%d')
        return f'sms_daily_count_{date_str}_{phone}'
    
    @classmethod
    def can_send(cls, phone):
        """
        检查是否可以发送短信
        
        Returns:
            tuple: (can_send: bool, message: str)
        """
        # 检查发送频率限制
        last_send_time = cache.get(cls._get_send_time_key(phone))
        if last_send_time and (time.time() - last_send_time) < cls.SEND_INTERVAL:
            wait_time = int(cls.SEND_INTERVAL - (time.time() - last_send_time))
            return False, f'发送过于频繁，请等待{wait_time}秒'
        
        # 检查每日发送次数限制
        daily_count = cache.get(cls._get_daily_count_key(phone), 0)
        if daily_count >= cls.DAILY_LIMIT:
            return False, '今日发送次数已达上限，请明天再试'
        
        return True, '可以发送'
    
    @classmethod
    def send_sms(cls, phone, code_type, code=None):
        """
        发送短信验证码
        
        Args:
            phone: 手机号码
            code_type: 验证码类型
            code: 验证码（可选，不传则自动生成）
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # 检查是否可以发送
        can_send, message = cls.can_send(phone)
        if not can_send:
            return False, message
        
        # 生成或接收验证码
        if code is None:
            code = cls.generate_code()
        
        # 保存到缓存
        cache_key = cls._get_cache_key(phone, code_type)
        cache.set(cache_key, code, cls.CODE_EXPIRE_TIME)
        
        # 记录发送时间
        cache.set(cls._get_send_time_key(phone), time.time(), cls.SEND_INTERVAL * 2)
        
        # 增加每日发送次数
        daily_count_key = cls._get_daily_count_key(phone)
        daily_count = cache.get(daily_count_key, 0)
        cache.set(daily_count_key, daily_count + 1, 86400)  # 24 小时
        
        # TODO: 调用真实的短信服务商 API 发送短信
        # 示例代码（以阿里云为例）：
        # from aliyunsdkcore.client import AcsClient
        # from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
        # 
        # client = AcsClient(settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET, 'cn-hangzhou')
        # request = SendSmsRequest()
        # request.set_PhoneNumbers(phone)
        # request.set_SignName('您的签名')
        # request.set_TemplateCode('您的模板代码')
        # request.set_TemplateParam(f'{{"code":"{code}"}}')
        # response = client.do_action_with_exception(request)
        
        # 开发环境打印验证码（方便测试）
        print(f"\n{'='*60}")
        print(f"【短信验证码】手机号：{phone}, 类型：{code_type}, 验证码：{code}")
        print(f"{'='*60}\n")
        
        return True, '验证码已发送'
    
    @classmethod
    def verify_code(cls, phone, code_type, code):
        """
        验证短信验证码
        
        Args:
            phone: 手机号码
            code_type: 验证码类型
            code: 验证码
            
        Returns:
            tuple: (valid: bool, message: str)
        """
        cache_key = cls._get_cache_key(phone, code_type)
        stored_code = cache.get(cache_key)
        
        if stored_code is None:
            return False, '验证码已过期或不存在'
        
        if stored_code != code:
            return False, '验证码错误'
        
        # 验证成功后删除验证码，防止重复使用
        cache.delete(cache_key)
        
        return True, '验证成功'
    
    @classmethod
    def clear_codes(cls, phone):
        """清除某个手机号的所有验证码"""
        for code_type in [cls.TYPE_LOGIN, cls.TYPE_RESET_PASSWORD, cls.TYPE_CHANGE_PHONE]:
            cache_key = cls._get_cache_key(phone, code_type)
            cache.delete(cache_key)


def validate_phone_number(phone):
    """
    验证手机号码格式是否正确
    
    Args:
        phone: 手机号码字符串
        
    Returns:
        tuple: (valid: bool, message: str)
    """
    import re
    
    if not phone:
        return False, '手机号不能为空'
    
    # 中国大陆手机号正则表达式
    pattern = r'^1[3-9]\d{9}$'
    
    if not re.match(pattern, phone):
        return False, '手机号格式不正确'
    
    return True, '手机号格式正确'
