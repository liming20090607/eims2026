# 真正的微信扫码登录实现指南

## 概述

本文档介绍如何实现真正的微信开放平台扫码登录功能，与之前实现的通用二维码登录不同，这个方案使用微信官方的OAuth2.0授权机制。

## 核心区别

### 之前的通用二维码登录（qr-login）
- ✅ 无需第三方平台注册
- ✅ 立即可用
- ❌ 需要手动扫描二维码并输入账号密码
- ❌ 不是真正的"微信"登录

### 真正的微信扫码登录（wechat-login）
- ✅ 使用微信官方JS-SDK
- ✅ 微信内直接授权，无需输入密码
- ✅ 首次绑定后，后续可直接扫码登录
- ❌ 需要注册微信开放平台
- ❌ 需要公网可访问的域名

## 实现步骤

### 第一步：注册微信开放平台

1. **访问微信开放平台**
   - 网址：https://open.weixin.qq.com/
   
2. **注册开发者账号**
   - 需要准备：企业营业执照、对公账户
   - 个人无法注册网站应用
   
3. **认证开发者资质**
   - 费用：300元/年
   - 审核时间：1-5个工作日

### 第二步：创建网站应用

1. **进入管理中心**
   - 点击"管理中心" -> "网站应用" -> "创建网站应用"

2. **填写应用信息**
   ```
   应用名称：协同AI办公系统
   应用简介：企业内部办公管理系统
   应用官网：https://your-domain.com
   应用图标：上传Logo（建议108x108px）
   ```

3. **填写开发信息**
   ```
   授权回调域：your-domain.com
   （注意：不要带http://或https://，只填域名）
   ```

4. **提交审核**
   - 审核时间：1-7个工作日
   - 审核通过后获得AppID和AppSecret

### 第三步：配置系统参数

1. **获取凭证**
   - AppID：应用唯一标识
   - AppSecret：应用密钥（妥善保管）

2. **配置到系统**
   
   方法一：修改 `.env` 文件（推荐）
   ```env
   WECHAT_OPEN_APP_ID=your_app_id_here
   WECHAT_OPEN_APP_SECRET=your_app_secret_here
   WECHAT_OPEN_REDIRECT_URI=https://your-domain.com/wechat-login/callback/
   ```
   
   方法二：直接修改 `settings.py`
   ```python
   WECHAT_OPEN_APP_ID = 'your_app_id_here'
   WECHAT_OPEN_APP_SECRET = 'your_app_secret_here'
   WECHAT_OPEN_REDIRECT_URI = 'https://your-domain.com/wechat-login/callback/'
   ```

3. **重启服务器**
   ```bash
   python manage.py runserver 8000
   ```

### 第四步：配置授权回调域名

**重要**：微信要求回调域名必须是：
- ✅ 公网可访问
- ✅ 已备案（中国大陆服务器）
- ✅ HTTPS协议（推荐）

**开发环境解决方案**：

1. **使用内网穿透工具**（推荐用于测试）
   ```bash
   # 安装 ngrok
   npm install -g ngrok
   
   # 启动内网穿透
   ngrok http 8000
   ```
   会生成类似 `https://abc123.ngrok.io` 的临时域名
   
2. **配置微信开放平台**
   - 授权回调域：abc123.ngrok.io
   - 修改 .env 中的 REDIRECT_URI

3. **本地hosts配置**（仅用于测试）
   ```
   # 在 C:\Windows\System32\drivers\etc\hosts 添加
   127.0.0.1 your-test-domain.com
   ```

### 第五步：测试流程

1. **访问登录页面**
   ```
   http://127.0.0.1:8000/login/
   ```

2. **点击"微信扫码登录"**
   - 页面会显示微信官方二维码
   - 二维码由微信JS-SDK生成

3. **用微信扫描二维码**
   - 打开微信 -> 发现 -> 扫一扫
   - 扫描屏幕上的二维码

4. **手机端确认授权**
   - 首次使用：显示授权确认页面
   - 点击"确认登录"

5. **首次绑定账号**
   - 如果是第一次使用，会跳转到绑定页面
   - 输入系统用户名和密码
   - 点击"确认绑定"

6. **完成登录**
   - 绑定成功后自动登录
   - 跳转到系统首页
   - 下次扫码可直接登录，无需再绑定

## 技术架构

### 数据模型

1. **WechatUserBinding** - 微信用户绑定关系
   ```python
   - user: 关联的系统用户
   - openid: 微信OpenID（唯一标识）
   - unionid: 微信UnionID（同一主体下的统一标识）
   - nickname: 微信昵称
   - headimgurl: 微信头像
   - is_bound: 是否已绑定
   - bind_time: 绑定时间
   - last_login_time: 最后登录时间
   ```

2. **WechatQRCodeSession** - 扫码会话
   ```python
   - session_id: 会话UUID
   - state: 防CSRF的随机字符串
   - status: 状态（pending/scanned/authorized/bound）
   - code: 微信返回的授权码
   - openid: 微信OpenID
   - user: 绑定的用户
   ```

### API流程

```
1. 电脑端请求二维码
   GET /wechat-login/
   ↓
   创建WechatQRCodeSession
   生成state参数
   返回微信授权URL

2. 微信JS-SDK渲染二维码
   用户扫描二维码
   ↓
   微信服务器记录扫码事件

3. 用户在手机端确认授权
   微信重定向到回调地址
   GET /wechat-login/callback/?code=xxx&state=xxx
   ↓
   验证state参数
   通过code换取access_token和openid
   查询WechatUserBinding

4a. 已绑定用户
   直接登录系统
   跳转到首页

4b. 未绑定用户
   显示绑定页面
   用户输入账号密码
   POST /wechat-login/bind/
   ↓
   验证账号密码
   创建WechatUserBinding
   登录系统
   跳转到首页
```

### 安全机制

1. **State参数防CSRF**
   - 每次生成二维码时创建随机state
   - 回调时验证state是否匹配
   - 防止跨站请求伪造攻击

2. **OpenID唯一性**
   - OpenID是用户在当前应用的唯一标识
   - 一个OpenID只能绑定一个系统账号
   - 防止账号冲突

3. **HTTPS传输**
   - 生产环境必须使用HTTPS
   - 保护access_token和用户信息

4. **Token有效期管理**
   - access_token有效期2小时
   - refresh_token有效期30天
   - 过期后需要重新授权

## URL路由

```python
/wechat-login/                              # 微信扫码登录页面
/wechat-login/callback/                     # 微信授权回调
/wechat-login/bind/                         # 绑定账号页面
/wechat-login/status/<session_id>/          # 检查登录状态（AJAX）
/wechat-login/unbind/                       # 解绑微信（POST）
/wechat-login/my-bindings/                  # 查看我的绑定
```

## 常见问题

### Q1: 二维码显示失败？
**A**: 检查以下几点：
- AppID是否正确配置
- 网络是否可以访问微信服务器
- 浏览器控制台是否有错误
- 微信JS-SDK是否正确加载

### Q2: 扫码后没有反应？
**A**: 可能原因：
- 授权回调域配置错误
- 回调地址不可访问（需要公网IP）
- state参数不匹配
- 检查服务器日志

### Q3: 提示"redirect_uri参数错误"？
**A**: 
- 检查WECHAT_OPEN_REDIRECT_URI配置
- 确保与微信开放平台配置的域名一致
- 注意URL编码问题

### Q4: 如何更换绑定的微信？
**A**: 
- 访问 `/wechat-login/my-bindings/`
- 点击"解绑"按钮
- 重新扫码绑定新微信

### Q5: 一个微信可以绑定多个账号吗？
**A**: 
- 不可以，一个OpenID只能绑定一个账号
- 如需切换，先解绑再重新绑定

### Q6: 开发环境如何测试？
**A**: 
- 使用ngrok等内网穿透工具
- 或使用云服务器部署测试环境
- 微信不支持localhost或127.0.0.1

## 生产环境部署

### 必要条件

1. **域名备案**
   - 中国大陆服务器必须备案
   - 备案后才能配置到微信开放平台

2. **HTTPS证书**
   - 推荐使用Let's Encrypt免费证书
   - 或使用云服务商提供的SSL证书

3. **固定公网IP**
   - 不能使用动态IP
   - 建议使用云服务器

### 配置示例

```python
# settings.py (生产环境)

WECHAT_OPEN_APP_ID = os.getenv('WECHAT_OPEN_APP_ID')
WECHAT_OPEN_APP_SECRET = os.getenv('WECHAT_OPEN_APP_SECRET')
WECHAT_OPEN_REDIRECT_URI = 'https://eims.yourcompany.com/wechat-login/callback/'

# 安全设置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Nginx配置

```nginx
server {
    listen 443 ssl;
    server_name eims.yourcompany.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 进阶功能

### 1.  UnionID机制

如果公司有多个应用（公众号、小程序、网站），可以使用UnionID打通用户：

```python
# 通过UnionID查找用户
binding = WechatUserBinding.objects.filter(unionid=unionid).first()
```

### 2. 自动创建账号

首次扫码时自动创建系统账号：

```python
if not user:
    # 自动生成用户名
    username = f"wx_{openid[:8]}"
    user = User.objects.create_user(
        username=username,
        password=make_random_password(),
        first_name=nickname
    )
    # 绑定微信
    WechatUserBinding.bind_user(user, openid, unionid, ...)
```

### 3. 微信信息同步

定期同步微信用户信息：

```python
def sync_wechat_userinfo(binding):
    result = wechat_service.get_user_info(access_token, binding.openid)
    if result['success']:
        binding.nickname = result['nickname']
        binding.headimgurl = result['headimgurl']
        binding.save()
```

### 4. 多微信绑定

允许一个账号绑定多个微信：

```python
# 修改模型，去掉openid的唯一约束
# 添加 unique_together = ['user', 'openid']
```

## 相关文件

- 模型：`eims_app/models/model_wechat_binding.py`
- 服务：`eims_app/services/wechat_service.py`
- 视图：`eims_app/views/views_wechat_login.py`
- 模板：
  - `eims_app/templates/auth/wechat_qr_login.html`
  - `eims_app/templates/auth/wechat_bind_account.html`
  - `eims_app/templates/auth/wechat_my_bindings.html`
  - `eims_app/templates/auth/wechat_login_error.html`
  - `eims_app/templates/auth/wechat_login_config_error.html`
- URL：`eims_app/urls.py`
- 配置：`settings.py`

## 总结

真正的微信扫码登录提供了更好的用户体验：
- ✅ 无需记忆密码
- ✅ 一键授权登录
- ✅ 安全可靠
- ✅ 符合用户使用习惯

但需要投入一定成本：
- 💰 微信开放平台认证费：300元/年
- ⏱️ 审核时间：1-7个工作日
- 🌐 需要公网域名和HTTPS

对于企业内部系统，建议优先实现此功能以提升用户体验。
