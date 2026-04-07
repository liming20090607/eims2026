# 云服务器 CSRF 403 错误修复指南

## 🔍 问题描述

在云服务器（39.106.41.239:8000）上访问协同办公系统时，出现以下错误：

```
禁止访问 (403)
CSRF验证失败. 请求被中断.

Reason given for failure:
CSRF token from POST incorrect.
```

**受影响的功能**：所有需要 POST 请求的页面（如新增产值回款、编辑项目等）

---

## ✅ 问题原因

Django 的 CSRF（跨站请求伪造）保护机制要求所有请求的来源必须在 `CSRF_TRUSTED_ORIGINS` 中注册。当前配置缺少云服务器 IP 地址。

---

## 🔧 修复步骤

### 步骤 1：SSH 登录云服务器

```bash
ssh root@39.106.41.239
```

### 步骤 2：进入项目目录并拉取最新代码

```bash
cd /var/www/eims
git pull gitee master
```

### 步骤 3：验证设置文件

检查 `settings.py` 文件是否包含以下内容（应该在文件顶部附近）：

```python
# CSRF 信任来源（生产环境配置）
CSRF_TRUSTED_ORIGINS = [
    'http://39.106.41.239',
    'http://39.106.41.239:8000',
    'http://localhost',
    'http://127.0.0.1',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

### 步骤 4：重启服务

**如果使用 Supervisor 管理服务：**

```bash
supervisorctl restart eims
```

**或者直接重启 Django 服务：**

```bash
# 如果使用 Gunicorn
supervisorctl restart gunicorn

# 如果使用 runserver（开发环境）
# 找到进程并重启
ps aux | grep python
kill -9 <进程ID>
python manage.py runserver 0.0.0.0:8000 &
```

### 步骤 5：验证修复

1. **清除浏览器缓存和 Cookie**
   - 打开浏览器开发者工具（F12）
   - Application → Storage → Clear site data
   - 或者直接使用隐私模式/无痕模式

2. **重新访问系统**
   ```
   http://39.106.41.239:8000/login/
   ```

3. **测试 POST 功能**
   - 登录后尝试访问"新增产值回款"页面
   - 填写表单并提交
   - 确认不再出现 403 错误

---

## 🎯 如果问题仍然存在

### 检查点 1：确认设置已生效

在服务器上查看设置文件：

```bash
cd /var/www/eims
grep -A 10 "CSRF_TRUSTED_ORIGINS" settings.py
```

应该显示包含 `39.106.41.239` 的配置。

### 检查点 2：确认服务已重启

```bash
# 查看 Supervisor 状态
supervisorctl status

# 查看进程是否正在运行
ps aux | grep python
```

### 检查点 3：查看 Django 日志

```bash
# 查看最近的错误日志
tail -f /var/www/eims/logs/error.log

# 或者查看 Supervisor 日志
supervisorctl tail eims stderr
```

### 检查点 4：浏览器端调试

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 提交表单时查看请求头
4. 确认 `Referer` 和 `Origin` 头是否正确

---

## 🔐 安全建议（生产环境）

当前配置使用了 `ALLOWED_HOSTS = ['*']`，这在生产环境中**不安全**。建议修改为：

```python
# settings.py

# 仅允许特定的主机访问
ALLOWED_HOSTS = [
    '39.106.41.239',
    'localhost',
    '127.0.0.1',
    # 如果有域名，添加域名
    # 'xietongai.com.cn',
    # 'www.xietongai.com.cn',
]

# CSRF 信任来源
CSRF_TRUSTED_ORIGINS = [
    'http://39.106.41.239',
    'http://39.106.41.239:8000',
    'http://localhost',
    'http://127.0.0.1',
    # 如果使用 HTTPS，添加 https 版本
    # 'https://xietongai.com.cn',
]
```

---

## 📝 其他常见问题

### Q1: 为什么登录后立即出现 403 错误？

**原因**：Django 在用户登录时会旋转（rotate）CSRF token 以提高安全性。如果登录后立即提交表单，可能使用的是旧的 token。

**解决**：登录后刷新页面再操作。

### Q2: 使用域名后还需要修改吗？

**是的**，如果使用域名（如 `xietongai.com.cn`），需要添加：

```python
CSRF_TRUSTED_ORIGINS = [
    'http://xietongai.com.cn',
    'https://xietongai.com.cn',  # 如果启用 HTTPS
    # ... 其他配置
]
```

### Q3: 如何临时禁用 CSRF 保护（仅用于调试）？

⚠️ **警告：仅用于调试，生产环境绝不能这样做！**

在视图函数上添加装饰器：

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def your_view(request):
    # 你的代码
    pass
```

---

## ✅ 验证清单

部署完成后，请确认以下各项：

- [ ] 代码已拉取到服务器（`git pull`）
- [ ] `settings.py` 包含 `CSRF_TRUSTED_ORIGINS` 配置
- [ ] 服务已重启（`supervisorctl restart`）
- [ ] 浏览器缓存已清除
- [ ] 登录功能正常
- [ ] 新增产值回款功能正常
- [ ] 其他 POST 请求功能正常

---

## 📞 获取帮助

如果按照以上步骤仍然无法解决问题，请提供以下信息：

1. 服务器操作系统版本：`cat /etc/os-release`
2. Python 版本：`python --version`
3. Django 版本：`python -m django --version`
4. 错误日志内容：`tail -100 /var/www/eims/logs/error.log`
5. `settings.py` 中 CSRF 相关配置

---

**修复日期**：2026-03-21  
**版本**：v1.0  
**作者**：EIMS 开发团队
