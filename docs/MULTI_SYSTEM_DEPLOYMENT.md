# 多系统架构部署指南

## 概述

本文档说明如何将 EIMS2026 单实例系统部署为四个独立的办公系统：

1. **eims_dingce** - 广西鼎策工程顾问有限责任公司系统 (`/dingce/`)
2. **eims_shengchang** - 广西晟昌工程科技有限责任公司系统 (`/shengchang/`)
3. **eims_jiachengda** - 广西嘉诚达工程造价咨询有限公司系统 (`/jiachengda/`)
4. **eims_root_admin** - 超级管理员后台系统 (`/root/`)

所有系统通过同一端口、不同URL路径访问，实现完全数据隔离。

---

## 系统架构

### 目录结构
```
E:/EIMS2026/
├── eims_app/                 # 共享工具库（中间件、路由器等）
├── eims_dingce/              # 鼎策公司系统
├── eims_shengchang/          # 晟昌公司系统
├── eims_jiachengda/          # 嘉诚达公司系统
├── eims_root_admin/          # Root超级管理员后台
├── settings.py               # 统一配置文件
├── urls.py                   # 路由分发配置
└── ...其他共享文件
```

### 数据库架构
- `eims_dingce` - 鼎策公司独立数据库
- `eims_shengchang` - 晟昌公司独立数据库
- `eims_jiachengda` - 嘉诚达公司独立数据库
- `eims_root` - Root后台管理数据库

### 智能路由逻辑
```
用户访问根路径 (/) 
    ↓
检查登录状态
    ↓
未登录 → 跳转登录页 (/login/)
    ↓
已登录 → 检查用户类型
    ├─ Superuser → /root/ (Root后台)
    ├─ 单公司用户 → 自动跳转到对应公司系统
    └─ 多公司用户 → 显示公司选择页面
```

---

## 部署步骤

### 第一步：创建数据库

运行SQL脚本创建四个独立数据库：

```bash
mysql -u root -p < create_multi_system_databases.sql
```

或手动执行：
```sql
CREATE DATABASE IF NOT EXISTS eims_dingce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_shengchang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_jiachengda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_root CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 第二步：验证配置

运行测试脚本验证所有配置是否正确：

```bash
python test_multi_system.py
```

预期输出：所有测试项显示"✓ 通过"

### 第三步：执行数据库迁移

运行迁移脚本在所有数据库中创建表结构：

```bash
python run_multi_system_migrations.py
```

这将依次为四个数据库执行 `migrate` 命令。

### 第四步：创建超级管理员

在 root 数据库中创建超级管理员账号：

```bash
python manage.py createsuperuser --database=root_admin
```

按提示输入用户名、邮箱和密码。

### 第五步：初始化公司数据（可选）

如需在各公司数据库中预置基础数据，可运行：

```bash
python init_multi_system.py
```

这会为每个公司系统设置默认配置。

### 第六步：启动服务器

```bash
python manage.py runserver
```

或使用生产环境启动：
```bash
python start_server.py
```

---

## 访问方式

### 本地开发环境

- 鼎策系统：http://127.0.0.1:8000/dingce/
- 晟昌系统：http://127.0.0.1:8000/shengchang/
- 嘉诚达系统：http://127.0.0.1:8000/jiachengda/
- Root后台：http://127.0.0.1:8000/root/
- 智能路由：http://127.0.0.1:8000/ （根据用户权限自动跳转）

### 生产环境

假设服务器IP为 `39.106.41.239`：

- 鼎策系统：http://39.106.41.239:8000/dingce/
- 晟昌系统：http://39.106.41.239:8000/shengchang/
- 嘉诚达系统：http://39.106.41.239:8000/jiachengda/
- Root后台：http://39.106.41.239:8000/root/

---

## 用户权限规则

### 1. 超级管理员 (Superuser)
- 直接访问 `/root/` 后台管理系统
- 可查看所有公司的数据
- 可管理所有公司的用户和权限

### 2. 单公司用户
- 登录后自动跳转到所属公司系统
- 只能访问该公司的数据
- 无法看到其他公司信息

### 3. 多公司用户
- 登录后显示公司选择页面
- 用户手动选择要进入的公司系统
- 在不同公司间切换需重新选择

### 4. 无权限用户
- 显示"权限不足"页面
- 提示联系管理员分配权限

---

## 关键组件说明

### 1. 路径解析中间件
**文件**: `eims_app/middleware/path_resolver.py`

功能：
- 解析URL路径识别当前访问的系统
- 设置 `request.current_system` 标识
- 设置 `request.company_name` 公司名称

### 2. 数据库路由器
**文件**: `eims_app/utils/database_router.py`

功能：
- 根据 `request.current_system` 自动选择数据库
- 确保各公司数据完全隔离
- Root后台可跨数据库查询

### 3. 智能路由选择器
**文件**: `eims_app/views/views_router.py`

功能：
- 根据用户权限决定跳转目标
- 单公司用户自动跳转
- 多公司用户显示选择页面

### 4. 租户选择页面
**文件**: `eims_app/templates/eims_app/tenant_select.html`

功能：
- 美观的公司选择界面
- 显示用户可访问的所有公司
- 点击卡片直接进入对应系统

---

## 数据隔离机制

### 数据库层面
- 每个公司有独立的MySQL数据库
- 物理隔离，数据完全不交叉
- Root后台通过 `.using()` 方法跨库查询

### 应用层面
- 数据库路由器自动选择正确数据库
- 中间件确保请求上下文正确
- 视图函数无需手动指定数据库

### 会话管理
- Session在各系统间共享（使用同一Session表）
- 用户登录一次即可访问所有有权限的系统
- 登出后清除所有系统的会话

---

## 定制开发指南

### 为单个公司添加新功能

1. 在对应公司应用中修改代码
   ```
   eims_dingce/views/xxx.py
   eims_dingce/templates/eims_dingce/xxx.html
   ```

2. 仅在该公司的数据库中迁移
   ```bash
   python manage.py migrate --database=dingce
   ```

3. 其他公司不受影响

### 为所有公司添加通用功能

1. 在 `eims_app` 中开发通用模块
2. 在四个公司应用中分别引用
3. 在所有数据库中迁移

### Root后台扩展

Root后台位于 `eims_root_admin/`，可以：
- 查看所有公司数据统计
- 跨公司用户管理
- 全局权限配置
- 数据同步工具

---

## 故障排查

### 问题1：AlreadyRegistered 错误

**现象**: `django.contrib.admin.sites.AlreadyRegistered`

**原因**: 多个应用注册了相同的Admin模型

**解决**: 已运行 `fix_admin_conflicts.py`，公司应用的admin注册已被注释

### 问题2：数据库连接失败

**检查**:
```bash
mysql -u root -p -e "SHOW DATABASES LIKE 'eims_%';"
```

**解决**: 确保四个数据库都已创建

### 问题3：路由404错误

**检查**: 
- 确认 `urls.py` 中包含所有路由
- 确认各公司应用的 `urls.py` 存在且正确

**解决**: 运行 `python test_multi_system.py` 验证URL配置

### 问题4：静态文件加载失败

**解决**:
```bash
python manage.py collectstatic
```

---

## 备份与恢复

### 备份所有数据库

```bash
mysqldump -u root -p --databases eims_dingce eims_shengchang eims_jiachengda eims_root > backup_all_$(date +%Y%m%d).sql
```

### 单独备份某个公司

```bash
mysqldump -u root -p eims_dingce > backup_dingce_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
mysql -u root -p < backup_all_20260321.sql
```

---

## 性能优化建议

### 1. 数据库索引
为常用查询字段添加索引：
```sql
USE eims_dingce;
CREATE INDEX idx_tenant ON eims_app_projectdetail(tenant_id);
CREATE INDEX idx_personnel_code ON eims_app_personnel(personnel_code);
```

### 2. 缓存机制
在 `settings.py` 中添加缓存配置：
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. 静态文件CDN
生产环境建议使用CDN加速静态文件加载

---

## 安全注意事项

### 1. 生产环境配置
- 修改 `SECRET_KEY` 为强随机字符串
- 设置 `DEBUG = False`
- 配置正确的 `ALLOWED_HOSTS`
- 启用 `SESSION_COOKIE_SECURE = True` (HTTPS)

### 2. 数据库安全
- 为每个数据库创建独立的用户账号
- 限制远程访问权限
- 定期备份数据
- 启用SSL连接

### 3. 权限控制
- 定期审计用户权限
- 及时禁用离职员工账号
- Root账号严格保密
- 启用双因素认证（可选）

---

## 维护任务

### 日常维护
- 监控服务器资源使用
- 检查错误日志
- 验证备份完整性

### 月度维护
- 清理过期Session
- 优化数据库表
- 更新依赖包

### 季度维护
- 完整系统测试
- 安全漏洞扫描
- 性能评估和优化

---

## 技术支持

如遇问题，请检查：
1. 测试脚本输出：`python test_multi_system.py`
2. Django错误日志：`logs/` 目录
3. MySQL错误日志：`/var/log/mysql/error.log`

---

## 版本历史

- **v1.0** (2026-03-21): 初始多系统架构实现
  - 创建四个独立应用
  - 实现智能路由选择
  - 配置多数据库支持
  - 完成数据隔离机制

---

**文档最后更新**: 2026年3月21日
