# 微信扫码登录功能使用说明

## 功能概述

微信扫码登录功能允许用户通过手机扫描二维码快速登录电脑端系统，无需输入账号密码。

## 使用流程

### 1. 电脑端操作

1. 访问登录页面：http://127.0.0.1:8000/login/
2. 点击"扫码登录"按钮
3. 页面会显示一个二维码，有效期为10分钟
4. 等待手机扫码确认

### 2. 手机端操作

1. 使用手机浏览器扫描电脑端显示的二维码
   - 注意：目前使用的是普通二维码，不是微信专用二维码
   - 任何可以识别二维码的工具都可以使用
   
2. 扫码后会打开确认登录页面
   
3. 如果未登录，需要先登录账号
   
4. 登录后，会显示您的账号信息
   
5. 点击"确认登录"按钮

### 3. 自动完成

- 手机确认后，电脑端会自动检测到状态变化
- 显示"登录成功，正在跳转..."
- 自动跳转到系统首页

## 技术实现

### 核心组件

1. **模型**：`QRCodeLoginSession`
   - 存储二维码会话信息
   - 记录状态：pending（等待扫码）、scanned（已扫码）、confirmed（已确认）、cancelled（已取消）、expired（已过期）
   - 有效期：10分钟

2. **视图函数**：
   - `qr_login_page` - 电脑端显示二维码
   - `qr_login_scan` - 手机端扫码确认页面
   - `qr_login_confirm` - 确认登录（AJAX）
   - `qr_login_status` - 检查登录状态（AJAX轮询）
   - `qr_login_complete` - 完成登录并跳转
   - `qr_login_cancel` - 取消登录（AJAX）

3. **前端轮询**：
   - 电脑端每2秒检查一次登录状态
   - 实时显示当前状态

### URL路由

```
/qr-login/                              # 电脑端二维码页面
/qr-login/scan/{session_id}/            # 手机端扫码确认页面
/qr-login/confirm/                      # 确认登录接口
/qr-login/status/{session_id}/          # 查询状态接口
/qr-login/complete/{session_id}/        # 完成登录
/qr-login/cancel/                       # 取消登录
```

## 注意事项

1. **二维码有效期**：每个二维码有效期为10分钟，过期后需要刷新页面重新获取

2. **安全性**：
   - 每个二维码都有唯一的UUID标识
   - 只有登录用户才能确认登录
   - 确认后立即清除会话数据

3. **网络要求**：
   - 手机和电脑需要在同一网络环境下
   - 或者手机可以访问电脑的IP地址

4. **浏览器兼容性**：
   - 支持所有现代浏览器
   - 推荐使用Chrome、Firefox、Edge等

## 未来优化方向

1. **真正的微信扫码**：集成微信开放平台SDK，实现真正的微信扫码登录
2. **企业微信集成**：如果使用企业微信，可以集成企业微信的扫码登录
3. **钉钉集成**：同样可以集成钉钉的扫码登录
4. **自定义域名**：生产环境需要使用可公网访问的域名
5. **HTTPS支持**：生产环境必须使用HTTPS保证安全

## 故障排除

### 问题1：二维码无法识别
- 确保手机摄像头正常工作
- 调整手机与屏幕的距离
- 确保屏幕亮度足够

### 问题2：扫码后无法打开页面
- 检查网络连接
- 确认电脑IP地址是否正确
- 防火墙是否阻止了访问

### 问题3：确认后电脑端没有反应
- 检查浏览器控制台是否有错误
- 刷新页面重试
- 检查服务器日志

### 问题4：提示"二维码已过期"
- 刷新页面重新获取新的二维码
- 确保在10分钟内完成扫码和确认

## 开发说明

### 安装依赖

```bash
pip install qrcode[pil]==7.4.2
```

### 数据库迁移

```bash
python manage.py makemigrations eims_app
python manage.py migrate eims_app
```

### 测试流程

1. 访问 http://127.0.0.1:8000/login/
2. 点击"扫码登录"
3. 用手机扫描屏幕上的二维码
4. 在手机端确认登录
5. 观察电脑端是否自动跳转

## 相关文件

- 模型：`eims_app/models/model_qr_login.py`
- 视图：`eims_app/views/views_qr_login.py`
- 模板：
  - `eims_app/templates/auth/qr_login.html` - 电脑端二维码页面
  - `eims_app/templates/auth/qr_login_confirm.html` - 手机端确认页面
  - `eims_app/templates/auth/qr_login_expired.html` - 过期提示页面
  - `eims_app/templates/auth/qr_login_waiting.html` - 等待确认页面
  - `eims_app/templates/auth/qr_login_error.html` - 错误提示页面
- URL配置：`eims_app/urls.py`
- 登录页面：`eims_app/templates/login.html`
