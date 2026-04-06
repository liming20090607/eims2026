# 微信扫码登录 - 快速开始

## 🚀 5分钟快速体验（开发环境）

### 步骤1：安装依赖

```bash
pip install requests qrcode[pil]==7.4.2
```

### 步骤2：数据库迁移

```bash
python manage.py makemigrations eims_app
python manage.py migrate eims_app
```

### 步骤3：配置微信开放平台（可选，用于测试）

**如果没有微信开放平台账号**，可以先跳过此步，系统会显示配置提示页面。

**如果有账号**，在 `.env` 文件中添加：

```env
WECHAT_OPEN_APP_ID=wx1234567890abcdef
WECHAT_OPEN_APP_SECRET=your_secret_here
WECHAT_OPEN_REDIRECT_URI=http://your-domain.com/wechat-login/callback/
```

### 步骤4：启动服务器

```bash
python manage.py runserver 8000
```

### 步骤5：访问测试

1. 打开浏览器：http://127.0.0.1:8000/login/
2. 点击"微信扫码登录"按钮
3. 如果未配置，会看到配置说明页面
4. 如果已配置，会显示微信二维码

---

## 📋 完整实现清单

### ✅ 已完成的功能

- [x] 微信用户绑定模型（WechatUserBinding）
- [x] 微信扫码会话模型（WechatQRCodeSession）
- [x] 微信API服务类（WechatOpenPlatformService）
- [x] 扫码登录视图（views_wechat_login.py）
- [x] 微信扫码登录页面（wechat_qr_login.html）
- [x] 账号绑定页面（wechat_bind_account.html）
- [x] 绑定管理页面（wechat_my_bindings.html）
- [x] 错误提示页面
- [x] URL路由配置
- [x] Settings配置项
- [x] 登录页面入口

### 🔧 需要配置的项

1. **微信开放平台账号**
   - 注册：https://open.weixin.qq.com/
   - 认证费用：300元/年
   - 创建网站应用

2. **获取凭证**
   - AppID
   - AppSecret

3. **配置回调域名**
   - 必须是公网可访问的域名
   - 必须已备案（中国大陆）
   - 推荐使用HTTPS

4. **系统配置**
   ```python
   # settings.py 或 .env
   WECHAT_OPEN_APP_ID = 'your_app_id'
   WECHAT_OPEN_APP_SECRET = 'your_app_secret'
   WECHAT_OPEN_REDIRECT_URI = 'https://your-domain.com/wechat-login/callback/'
   ```

---

## 🎯 使用流程

### 首次使用

```
1. 访问登录页面
   ↓
2. 点击"微信扫码登录"
   ↓
3. 用微信扫描二维码
   ↓
4. 手机端确认授权
   ↓
5. 输入系统账号密码绑定
   ↓
6. 绑定成功，自动登录
```

### 后续使用

```
1. 访问登录页面
   ↓
2. 点击"微信扫码登录"
   ↓
3. 用微信扫描二维码
   ↓
4. 手机端确认授权
   ↓
5. 自动登录（无需输入密码）
```

---

## 🔗 相关URL

| URL | 说明 |
|-----|------|
| `/login/` | 登录页面（包含微信扫码入口） |
| `/wechat-login/` | 微信扫码登录页面 |
| `/wechat-login/callback/` | 微信授权回调地址 |
| `/wechat-login/bind/` | 绑定账号页面 |
| `/wechat-login/my-bindings/` | 查看我的微信绑定 |
| `/wechat-login/unbind/` | 解绑微信（POST） |

---

## 📊 两种登录方式对比

| 特性 | 通用二维码登录 | 微信扫码登录 |
|------|---------------|-------------|
| 第三方依赖 | ❌ 无 | ✅ 微信开放平台 |
| 配置难度 | ⭐ 简单 | ⭐⭐⭐ 较复杂 |
| 用户体验 | ⭐⭐ 需输密码 | ⭐⭐⭐⭐⭐ 一键授权 |
| 安全性 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 高 |
| 成本 | 💰 免费 | 💰💰 300元/年 |
| 适用场景 | 内部测试 | 生产环境 |

---

## ⚠️ 注意事项

1. **开发环境限制**
   - 微信不支持localhost
   - 需要使用内网穿透工具（如ngrok）
   - 或使用云服务器测试

2. **生产环境要求**
   - 必须有备案域名
   - 必须使用HTTPS
   - 必须有固定公网IP

3. **安全建议**
   - 妥善保管AppSecret
   - 不要提交到版本控制
   - 使用环境变量配置

4. **用户体验**
   - 首次使用需要绑定账号
   - 绑定后下次可直接扫码登录
   - 可以在个人中心管理绑定关系

---

## 🆘 常见问题

**Q: 没有微信开放平台账号怎么办？**  
A: 可以先使用通用二维码登录（/qr-login/），功能类似但不需要微信集成。

**Q: 开发环境如何测试？**  
A: 使用ngrok等内网穿透工具生成临时公网域名。

**Q: 一个微信可以绑定多个账号吗？**  
A: 不可以，一个OpenID只能绑定一个账号。

**Q: 如何更换绑定的微信？**  
A: 访问 `/wechat-login/my-bindings/` 解绑后重新绑定。

**Q: 扫码后提示"redirect_uri参数错误"？**  
A: 检查回调地址配置是否与微信开放平台一致。

---

## 📚 详细文档

- 完整实现指南：[WECHAT_LOGIN_GUIDE.md](WECHAT_LOGIN_GUIDE.md)
- 通用二维码登录：[QR_LOGIN_README.md](QR_LOGIN_README.md)

---

## 🎉 总结

微信扫码登录已完整实现，包括：
- ✅ 完整的OAuth2.0授权流程
- ✅ 账号绑定和解绑功能
- ✅ 安全的state防CSRF机制
- ✅ 美观的用户界面
- ✅ 详细的错误提示

只需配置微信开放平台参数即可投入使用！
