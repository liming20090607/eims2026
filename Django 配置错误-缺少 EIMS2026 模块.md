# Django 配置错误 - 缺少 EIMS2026 模块

## ❌ 错误原因

**错误日志显示：**
```
ModuleNotFoundError: No module named 'EIMS2026'
```

**说明：**
- Django 在尝试导入 `EIMS2026` 模块
- 但这个模块不存在
- 可能是 `settings.py` 中的 `ROOT_URLCONF` 配置错误

---

## 🔍 需要检查配置

### 步骤 1：上传配置检查脚本

**双击：**
```
E:\EIMS2026\bat\upload-check-settings.bat
```

---

### 步骤 2：SSH 登录

**输入：**
```bash
ssh root@39.106.41.239
```

---

### 步骤 3：检查配置

**输入：**
```bash
bash /tmp/check-settings.sh
```

**脚本会显示：**
1. ✅ ROOT_URLCONF 配置
2. ✅ sys.path 配置
3. ✅ BASE_DIR 设置
4. ✅ 项目结构
5. ✅ urls.py 是否存在
6. ✅ wsgi.py 配置

---

### 步骤 4：复制输出给我

**执行后：**
1. 选中所有输出
2. Ctrl+C 复制
3. 粘贴给我

**我会根据配置提供修复方案！**

---

## 💡 可能的解决方案

### 方案 1：修改 ROOT_URLCONF

**如果 settings.py 中：**
```python
ROOT_URLCONF = 'EIMS2026.urls'
```

**应该改为：**
```python
ROOT_URLCONF = 'urls'
```

**或者：**
```python
ROOT_URLCONF = 'eims.urls'
```

---

### 方案 2：添加项目目录到 Python path

**如果项目目录结构不对，需要：**

```python
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
```

---

### 方案 3：检查 wsgi.py

**wsgi.py 应该这样配置：**

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()
```

---

## 📊 项目结构检查

**正确的项目结构应该是：**

```
/var/www/eims/
├── manage.py
├── settings.py
├── urls.py          ← 必须存在
├── wsgi.py
├── venv/
└── logs/
```

---

## 🎯 立即操作

**现在执行：**

1. **双击：** `upload-check-settings.bat`
2. **SSH 登录：** `ssh root@39.106.41.239`
3. **输入：** `bash /tmp/check-settings.sh`
4. **复制输出给我**

**我会根据实际配置提供精确的修复方案！**

---

## 📁 我已创建的工具

### 检查工具
- ✅ [`bat\check-settings.sh`](file://e:\EIMS2026\bat\check-settings.sh) - 检查 Django 配置
- ✅ [`bat\upload-check-settings.bat`](file://e:\EIMS2026\bat\upload-check-settings.bat) - 自动上传

### 说明文档
- **Django 配置错误.md** - 本文档

---

**预计时间：** 2-3 分钟  
**难度：** ⭐⭐（需要查看配置）

---

**最后更新：** 2026-04-03  
**服务器：** 39.106.41.239
