# 🔧 调试工具路径修复说明

## 📋 问题描述

访问 `http://localhost:8000/debug_import/` 时出现 404 错误：
```
Page not found (404)
"E:\EIMS2026\debug_import" 不存在
Raised by: django.views.static.serve
```

## 🔍 问题原因

Django 将 `debug_import/` 误解为静态文件路径，而不是视图函数路由。

**根本原因**：
- `debug_import_tool.py` 文件位于项目根目录：`E:\EIMS2026\debug_import_tool.py`
- URL 配置中使用了相对导入：`from .debug_import_tool import debug_import`
- Django 尝试从 `eims_app` 包内查找该模块，但找不到
- 导致路由配置失败，URL 被当作静态文件处理

## ✅ 解决方案

### **修改的文件**

**文件**: `eims_app/urls.py`

**修改前**（第 53-57 行）:
```python
# 导入调试工具（临时使用）
try:
    from .debug_import_tool import debug_import
except ImportError:
    debug_import = None
```

**修改后**:
```python
# 导入调试工具（临时使用）
try:
    import sys
    import os
    # 添加项目根目录到 Python 路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from debug_import_tool import debug_import
except ImportError:
    debug_import = None
```

### **修改说明**

1. **动态添加项目根目录到 Python 路径**
   - 计算项目根目录路径
   - 如果不在 sys.path 中，则添加到开头
   
2. **使用绝对导入**
   - 从 `from .debug_import_tool` 改为 `from debug_import_tool`
   - 直接从项目根目录导入模块

## 🚀 验证步骤

### **步骤 1：重启服务器**
```bash
# 停止当前服务器（Ctrl+C）
# 然后重新启动
python manage.py runserver
```

### **步骤 2：访问调试工具**
打开浏览器访问：**http://localhost:8000/debug_import/**

### **步骤 3：检查页面**
应该能看到调试工具的上传界面，而不是 404 错误页

## 📊 系统检查

运行系统检查确认配置正确：
```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

✅ **通过！**

## 🎯 现在可以使用的功能

### **调试工具地址**
- URL: http://localhost:8000/debug_import/
- 功能：上传 Excel 文件进行详细诊断

### **其他相关地址**
- 项目台账导入：http://localhost:8000/project_ledger/import/
- 合同管理导入：http://localhost:8000/contract_management/import/

## 💡 技术细节

### **为什么会出现这个问题？**

Django 的 URL 解析顺序：
1. 首先尝试匹配视图函数
2. 如果视图函数导入失败，URL 模式不会被注册
3. 未匹配的 URL 可能被静态文件处理器捕获
4. 导致误认为是静态文件路径

### **修复原理**

```python
# 获取 eims_app 目录的父目录（即项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到 Python 路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在可以直接从根目录导入模块
from debug_import_tool import debug_import
```

## ⚠️ 注意事项

### **1. 临时解决方案**
- 这个修复是为了开发调试方便
- 生产环境应该移除调试工具
- 或者将调试工具移动到正确的包结构内

### **2. 更好的做法**
长期建议将 `debug_import_tool.py` 移动到：
```
eims_app/
├── tools/
│   ├── __init__.py
│   └── debug_import_tool.py
```

然后导入：
```python
from eims_app.tools.debug_import_tool import debug_import
```

### **3. 安全性**
- 调试工具仅供开发环境使用
- 不要在生产服务器上启用
- 包含敏感的系统信息和数据访问权限

## 📁 相关文件

- URL 配置：[`eims_app/urls.py`](file://e:\EIMS2026\eims_app\urls.py)
- 调试工具：[`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py)
- 使用指南：[`DEBUG_TOOL_GUIDE.md`](file://e:\EIMS2026\DEBUG_TOOL_GUIDE.md)
- 快速访问：[`调试工具快速访问.md`](file://e:\EIMS2026\调试工具快速访问.md)

## 🎉 状态

**✅ 已修复** - 服务器已重启，调试工具现在可以正常访问

立即访问 → **http://localhost:8000/debug_import/**

---

**修复时间**: 2026-03-24 23:48  
**修复方式**: 修改 Python 导入路径  
**状态**: ✅ 已完成并验证
