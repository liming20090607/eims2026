# 手机短信验证登录功能实现说明

## 📋 功能概述

本系统实现了完整的手机短信验证功能，包括：

1. **短信验证码登录** - 用户可以使用手机号 + 验证码登录
2. **手机绑定** - 用户可以将手机号绑定到账号
3. **短信验证修改密码** - 通过短信验证码重置密码
4. **短信验证修改手机号** - 通过短信验证码修改绑定的手机号

## 🏗️ 系统架构

### 1. 数据模型

#### SMSVerificationRecord (短信验证记录)
**文件**: `eims_app/models/model_sms.py`

用于记录所有短信验证码的发送和验证历史，便于审计和日志追踪。

**主要字段**:
- `phone`: 手机号码
- `verification_type`: 验证类型（登录、重置密码、修改手机号）
- `verification_code`: 验证码（加密存储）
- `status`: 验证状态（成功、失败、过期）
- `user`: 关联用户
- `ip_address`: IP 地址
- `create_time`: 创建时间
- `expire_time`: 过期时间

### 2. 短信服务

**文件**: `eims_app/sms_service.py`

提供短信验证码的生成、发送、验证等功能。

**核心类**: `SMSService`

**主要功能**:
- `generate_code()`: 生成 6 位数字验证码
- `send_sms()`: 发送短信验证码
- `verify_code()`: 验证短信验证码
- `can_send()`: 检查是否可以发送（频率限制）

**安全机制**:
1. **验证码有效期**: 5 分钟
2. **发送频率限制**: 60 秒内只能发送一次
3. **每日发送次数限制**: 每个手机号每天最多 10 次
4. **一次性使用**: 验证成功后自动删除验证码

### 3. 视图函数

**文件**: `eims_app/views/views_sms_auth.py`

#### API 接口

1. **send_sms_code** - 发送短信验证码
   - URL: `/api/sms/send-code/`
   - 方法：POST
   - 参数：
     ```json
     {
       "phone": "13800138000",
       "code_type": "login"  // 或 reset_password, change_phone
     }
     ```

2. **sms_login** - 短信验证码登录
   - URL: `/api/sms/login/`
   - 方法：POST
   - 参数：
     ```json
     {
       "phone": "13800138000",
       "code": "123456"
     }
     ```

3. **change_phone** - 修改绑定手机号
   - URL: `/api/sms/change-phone/`
   - 方法：POST
   - 参数：
     ```json
     {
       "new_phone": "13900139000",
       "code": "123456"
     }
     ```

4. **reset_password_by_sms** - 短信验证重置密码
   - URL: `/api/sms/reset-password/`
   - 方法：POST
   - 参数：
     ```json
     {
       "phone": "13800138000",
       "code": "123456",
       "new_password": "newpassword123"
     }
     ```

### 4. 前端模板

**目录**: `eims_app/templates/sms_auth/`

#### forgot_password.html
忘记密码页面，包含三个步骤：
1. 输入手机号并发送验证码
2. 输入验证码和新密码
3. 完成提示

## 🚀 使用指南

### 方法一：通过 AJAX 调用（推荐）

#### 1. 发送验证码

```javascript
function sendVerificationCode(phone, codeType) {
    fetch('/api/sms/send-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            phone: phone,
            code_type: codeType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('验证码已发送');
            startCountdown(); // 开始倒计时
        } else {
            alert('发送失败：' + data.message);
        }
    });
}
```

#### 2. 短信验证码登录

```javascript
function smsLogin(phone, code) {
    fetch('/api/sms/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            phone: phone,
            code: code
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('登录成功');
            window.location.href = data.redirect_url || '/';
        } else {
            alert('登录失败：' + data.message);
        }
    });
}
```

#### 3. 重置密码

```javascript
function resetPassword(phone, code, newPassword) {
    fetch('/api/sms/reset-password/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            phone: phone,
            code: code,
            new_password: newPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('密码重置成功');
            window.location.href = '/login/';
        } else {
            alert('重置失败：' + data.message);
        }
    });
}
```

#### 4. 修改手机号

```javascript
function changePhone(newPhone, code) {
    fetch('/api/sms/change-phone/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            new_phone: newPhone,
            code: code
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('手机号修改成功');
            location.reload();
        } else {
            alert('修改失败：' + data.message);
        }
    });
}
```

### 方法二：通过表单提交

可以参考 `forgot_password.html` 模板中的完整实现。

## ⚙️ 配置说明

### 1. Django 缓存配置

短信验证码使用 Django 的 cache 系统存储，需要确保已配置缓存：

```python
# settings.py

# 开发环境使用本地内存缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
    }
}

# 生产环境建议使用 Redis 缓存
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }
```

### 2. 短信服务商配置（可选）

如果使用真实的短信服务商，需要在 `sms_service.py` 中配置：

```python
# 阿里云短信配置
ALIYUN_ACCESS_KEY_ID = 'your_access_key_id'
ALIYUN_ACCESS_KEY_SECRET = 'your_access_key_secret'
ALIYUN_SMS_SIGN_NAME = '您的签名'
ALIYUN_SMS_TEMPLATE_CODE = '您的模板代码'

# 腾讯云短信配置
TENCENT_SMS_APP_ID = 'your_app_id'
TENCENT_SMS_SECRET_KEY = 'your_secret_key'
TENCENT_SMS_SIGN_NAME = '您的签名'
```

## 🔒 安全注意事项

1. **验证码保护**
   - 验证码存储在服务器端缓存中，不暴露在客户端
   - 验证成功后立即删除，防止重复使用
   - 日志中只记录 `***`，不记录真实验证码

2. **频率限制**
   - 60 秒内只能发送一次
   - 每日最多 10 次
   - 防止恶意攻击

3. **IP 记录**
   - 记录每次请求的 IP 地址
   - 便于追踪异常行为

4. **手机号验证**
   - 使用正则表达式验证手机号格式
   - 只允许中国大陆手机号（1 开头，11 位）

## 📝 测试方法

### 开发环境测试

开发环境下，验证码会打印到控制台，方便测试：

```
============================================================
【短信验证码】手机号：13800138000, 类型：login, 验证码：123456
============================================================
```

### 生产环境测试

1. 配置真实的短信服务商 API
2. 使用真实手机号测试
3. 检查 `SMSVerificationRecord` 表查看发送记录

## 🔧 集成到现有系统

### 1. 在登录页面添加短信登录选项

修改 `eims_app/templates/login.html`，添加短信登录表单：

```html
<!-- 短信登录 -->
<div class="tab-pane fade" id="sms-login" role="tabpanel">
    <form id="sms-login-form">
        {% csrf_token %}
        <div class="mb-3">
            <label class="form-label">手机号</label>
            <div class="input-group">
                <input type="text" class="form-control" id="sms_phone" placeholder="请输入手机号">
                <button class="btn btn-outline-primary" type="button" id="send-code-btn">
                    获取验证码
                </button>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">验证码</label>
            <input type="text" class="form-control" id="sms_code" placeholder="请输入验证码">
        </div>
        <button type="submit" class="btn btn-primary w-100">登录</button>
    </form>
</div>
```

### 2. 在个人中心添加手机号绑定

修改 `eims_app/templates/profile.html`，添加手机号修改功能。

### 3. 在登录页面添加"忘记密码"链接

```html
<div class="mb-3">
    <a href="{% url 'eims_app:forgot_password' %}" class="text-muted">
        <small>忘记密码？</small>
    </a>
</div>
```

## 📊 数据统计

可以通过以下查询统计短信使用情况：

```python
from eims_app.models import SMSVerificationRecord
from django.utils import timezone
from datetime import timedelta

# 今日发送量
today = timezone.now().date()
today_count = SMSVerificationRecord.objects.filter(
    create_time__date=today
).count()

# 验证成功率
total_count = SMSVerificationRecord.objects.count()
success_count = SMSVerificationRecord.objects.filter(status='success').count()
success_rate = (success_count / total_count * 100) if total_count > 0 else 0

# 各类型验证分布
from django.db.models import Count
type_distribution = SMSVerificationRecord.objects.values(
    'verification_type'
).annotate(count=Count('id'))
```

## 🐛 常见问题

### 1. 验证码发送失败
- 检查手机号格式是否正确
- 检查是否超过发送频率限制
- 检查缓存配置是否正确

### 2. 验证码验证失败
- 检查验证码是否已过期（5 分钟）
- 检查验证码是否已被使用
- 检查缓存是否被清理

### 3. 生产环境无法发送短信
- 配置真实的短信服务商 API
- 检查 API 密钥是否正确
- 检查网络连接

## 📚 相关文件清单

### 后端文件
- `eims_app/models/model_sms.py` - 短信验证记录模型
- `eims_app/sms_service.py` - 短信服务工具
- `eims_app/views/views_sms_auth.py` - 短信认证视图
- `eims_app/models/__init__.py` - 模型导入配置
- `eims_app/urls.py` - URL 路由配置

### 前端文件
- `eims_app/templates/sms_auth/forgot_password.html` - 忘记密码页面

### 视图文件
- `eims_app/views/views_contract_management.py` - 添加 forgot_password 视图函数

## 🎯 后续优化建议

1. **图形验证码** - 在发送短信前增加图形验证码，防止机器刷短信
2. **语音验证码** - 提供语音验证码作为备选方案
3. **国际短信支持** - 支持国际手机号和短信服务
4. **短信模板管理** - 在后台管理短信模板和签名
5. **发送统计** - 统计短信发送量、成功率等指标
6. **黑名单机制** - 对恶意手机号加入黑名单

## 💡 技术支持

如需接入真实的短信服务，推荐以下服务商：

1. **阿里云短信** - https://www.aliyun.com/product/sms
2. **腾讯云短信** - https://cloud.tencent.com/product/sms
3. **华为云短信** - https://www.huaweicloud.com/product/msgsms.html
4. **容联云通讯** - https://www.yuntongxun.com/

---

**版本**: v1.0  
**创建时间**: 2026-03-21  
**最后更新**: 2026-03-21
