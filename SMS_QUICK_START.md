# 手机短信验证功能 - 快速使用指南

## ✅ 已完成配置

### 1. 数据库迁移
- ✅ 已创建 `SMSVerificationRecord` 模型
- ✅ 已执行数据库迁移

### 2. 后端配置
- ✅ 短信服务：`eims_app/sms_service.py`
- ✅ 数据模型：`eims_app/models/model_sms.py`
- ✅ 视图函数：`eims_app/views/views_sms_auth.py`
- ✅ URL 路由：已配置 5 个 API 接口

### 3. 前端模板
- ✅ 忘记密码页面：`eims_app/templates/sms_auth/forgot_password.html`

## 🚀 立即开始使用

### 方式一：访问忘记密码页面

直接在浏览器访问：`http://localhost:8000/forgot-password/`

页面功能：
1. 输入手机号
2. 获取短信验证码
3. 输入验证码和新密码
4. 完成密码重置

**注意**：开发环境下，验证码会打印到控制台（命令行），请注意查看！

### 方式二：通过 JavaScript 调用 API

#### 1. 发送验证码

```javascript
// 发送登录验证码
fetch('/api/sms/send-code/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({
        phone: '13800138000',  // 替换为实际手机号
        code_type: 'login'
    })
})
.then(response => response.json())
.then(data => {
    console.log(data);
    // 验证码会打印到控制台
});
```

#### 2. 短信登录

```javascript
fetch('/api/sms/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({
        phone: '13800138000',
        code: '123456'  // 替换为实际收到的验证码
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('登录成功');
        window.location.href = '/';
    }
});
```

#### 3. 重置密码

```javascript
fetch('/api/sms/reset-password/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({
        phone: '13800138000',
        code: '123456',
        new_password: 'newpassword123'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('密码重置成功');
        window.location.href = '/login/';
    }
});
```

#### 4. 修改手机号（需要先登录）

```javascript
fetch('/api/sms/change-phone/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({
        new_phone: '13900139000',
        code: '123456'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('手机号修改成功');
        location.reload();
    }
});
```

## 📱 测试流程

### 测试 1：忘记密码

1. 访问：`http://localhost:8000/forgot-password/`
2. 输入手机号（如：13800138000）
3. 点击"获取验证码"
4. **查看控制台（命令行）**，找到类似以下输出：
   ```
   ============================================================
   【短信验证码】手机号：13800138000, 类型：reset_password, 验证码：123456
   ============================================================
   ```
5. 在页面输入验证码
6. 输入新密码（至少 6 位）
7. 点击"重置密码"
8. 成功后会跳转到登录页面

### 测试 2：短信登录（需要集成到登录页面）

参考 `SMS_AUTH_IMPLEMENTATION.md` 文档中的"集成到现有系统"章节

### 测试 3：修改手机号（需要在个人中心集成）

1. 先登录系统
2. 访问个人中心
3. 点击"修改手机号"
4. 输入新手机号
5. 获取并输入验证码
6. 提交

## 🔍 查看验证记录

可以通过 Django shell 查看短信验证记录：

```bash
python manage.py shell
```

```python
from eims_app.models import SMSVerificationRecord

# 查看所有记录
records = SMSVerificationRecord.objects.all()
for r in records:
    print(f'{r.phone} - {r.verification_type} - {r.status} - {r.create_time}')

# 查看今天的记录
from django.utils import timezone
today = timezone.now().date()
today_records = SMSVerificationRecord.objects.filter(create_time__date=today)
print(f'今日发送了 {today_records.count()} 条短信')

# 查看成功率
total = SMSVerificationRecord.objects.count()
success = SMSVerificationRecord.objects.filter(status='success').count()
print(f'成功率：{success/total*100:.2f}%' if total > 0 else '无数据')
```

## ⚙️ 配置生产环境

### 1. 接入真实短信服务

编辑 `eims_app/sms_service.py`，找到 `send_sms` 方法中的 TODO 注释，替换为真实的短信 API：

```python
# 示例：阿里云短信
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

client = AcsClient(
    settings.ALIYUN_ACCESS_KEY_ID,
    settings.ALIYUN_ACCESS_KEY_SECRET,
    'cn-hangzhou'
)
request = SendSmsRequest()
request.set_PhoneNumbers(phone)
request.set_SignName('您的签名')
request.set_TemplateCode('您的模板代码')
request.set_TemplateParam(f'{{"code":"{code}"}}')
response = client.do_action_with_exception(request)
```

### 2. 配置缓存（推荐使用 Redis）

编辑 `settings.py`：

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. 配置短信服务商参数

在 `settings.py` 中添加：

```python
# 阿里云短信配置
ALIYUN_ACCESS_KEY_ID = 'your_access_key_id'
ALIYUN_ACCESS_KEY_SECRET = 'your_access_key_secret'
ALIYUN_SMS_SIGN_NAME = '您的签名'
ALIYUN_SMS_TEMPLATE_CODE = '您的模板代码'
```

## 📊 API 接口列表

| 接口 | URL | 方法 | 说明 |
|------|-----|------|------|
| 发送验证码 | `/api/sms/send-code/` | POST | 发送短信验证码 |
| 短信登录 | `/api/sms/login/` | POST | 验证码登录 |
| 重置密码 | `/api/sms/reset-password/` | POST | 短信验证重置密码 |
| 修改手机号 | `/api/sms/change-phone/` | POST | 短信验证修改手机号 |
| 忘记密码页面 | `/forgot-password/` | GET | 忘记密码页面 |

## 🔒 安全特性

1. ✅ 验证码 5 分钟过期
2. ✅ 60 秒发送频率限制
3. ✅ 每日最多 10 次发送
4. ✅ 验证码一次性使用
5. ✅ IP 地址记录
6. ✅ 完整的审计日志

## 🐛 开发环境特性

- ✅ 验证码打印到控制台（方便测试）
- ✅ 使用内存缓存（无需额外配置）
- ✅ 详细的错误提示

## 📚 完整文档

详细实现说明请参考：`SMS_AUTH_IMPLEMENTATION.md`

## 💡 下一步

1. **集成到登录页面** - 在登录页面添加"短信登录"选项卡
2. **集成到个人中心** - 在个人中心添加"修改手机号"功能
3. **接入真实短信服务** - 选择一家短信服务商并配置
4. **添加图形验证码** - 防止机器刷短信
5. **数据统计面板** - 在后台添加短信发送统计

## ❓ 常见问题

**Q: 为什么收不到短信？**
A: 开发环境下不会发送真实短信，验证码会打印到控制台。如需测试真实短信，需要接入短信服务商。

**Q: 验证码有效期是多久？**
A: 5 分钟。超过 5 分钟后会自动过期。

**Q: 可以多次使用同一个验证码吗？**
A: 不可以。验证成功后验证码会立即失效。

**Q: 如何查看发送记录？**
A: 可以通过 Django shell 查询 `SMSVerificationRecord` 模型。

**Q: 支持国际手机号吗？**
A: 当前版本仅支持中国大陆手机号（1 开头，11 位）。如需支持国际手机号，需要修改 `validate_phone_number` 函数。

---

**创建时间**: 2026-03-21  
**版本**: v1.0
