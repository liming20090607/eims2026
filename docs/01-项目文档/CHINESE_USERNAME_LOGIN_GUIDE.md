# ✅ 中文用户名登录系统 - 完整使用指南

## 📋 功能概述

本系统现已支持使用**中文姓名**作为登录凭证，同时保留原有的英文用户名登录方式。

---

## 🎯 支持的登录方式

用户可以使用以下**任意一种**方式登录：

| 登录方式 | 示例 | 说明 |
|---------|------|------|
| **用户名** | `zhangsan` | 英文用户名（拼音） |
| **中文姓名** ✨ | `张三` | 真实姓名（中文） |
| **邮箱** | `zhangsan@example.com` | 电子邮箱地址 |

---

## 🚀 快速开始

### **方式一：通过 Django Admin 后台设置**（推荐）

#### **步骤 1: 进入 Admin 后台**
访问：http://localhost:8000/admin/

使用超级管理员账号登录（默认：admin / admin123）

---

#### **步骤 2: 添加用户资料**

**方法 A - 通过"用户资料"管理**:
1. 点击左侧菜单的 **"用户资料"** (USER PROFILES)
2. 点击右上角的 **"+ 增加"** 按钮
3. 填写信息:
   ```
   用户：选择要设置的用户（下拉选择）
   姓名：输入中文姓名（如：张三）
   性别：可选
   生日：可选
   手机号：可选
   微信号：可选
   ```
4. 点击 **"保存"**

**方法 B - 通过"Users"管理**:
1. 点击左侧菜单的 **"Users"**
2. 点击要编辑的用户名
3. 滚动到页面底部，查看"姓名"字段
4. 点击页面上的 **"用户资料"** 链接进行编辑

---

#### **步骤 3: 验证登录**

设置完成后，返回登录页面：http://localhost:8000/login/

尝试使用以下方式登录：
- 用户名：`zhangsan`
- 姓名：`张三` ✨
- 邮箱：`zhangsan@example.com`

密码都是用户的原密码！

---

### **方式二：使用管理命令批量设置**

#### **单个用户设置**

```bash
python manage.py set_chinese_name --username zhangsan --name "张三"
```

**示例**:
```bash
# 为 admin 用户设置中文姓名
python manage.py set_chinese_name --username admin --name "管理员"

# 为 zhangsan 用户设置中文姓名
python manage.py set_chinese_name --username zhangsan --name "张三"
```

---

#### **批量导入（CSV 文件）**

**1. 创建 CSV 文件**

创建文件 `chinese_names.csv`，内容格式：
```csv
用户名，中文姓名
admin，管理员
zhangsan，张三
lisi，李四
wangwu，王五
```

**注意**: 
- 第一行必须是表头
- 使用 UTF-8 编码（可用 Excel 另存为 UTF-8 CSV）
- 逗号分隔

**2. 执行导入命令**

```bash
python manage.py set_chinese_name --file chinese_names.csv
```

**输出示例**:
```
✓ 创建并设置：admin -> 管理员
✓ 更新：zhangsan -> 张三
✓ 创建并设置：lisi -> 李四
✗ 用户不存在：wangwu

==================================================
完成！成功：3 条，失败：1 条
```

---

## 📖 详细使用说明

### **一、Admin 后台配置**

#### **UserProfile 管理界面**

访问：http://localhost:8000/admin/eims_app/userprofile/

**功能列表**:
1. ✅ **列表显示**
   - 用户名
   - 姓名（中文）
   - 性别
   - 手机号
   - 微信号

2. ✅ **搜索功能**
   - 可按用户名搜索
   - 可按中文姓名搜索
   - 可按手机号搜索

3. ✅ **筛选功能**
   - 按性别筛选

4. ✅ **批量导出**
   - 选中多个用户
   - 点击"导出选中的用户资料"
   - 下载 CSV 文件

---

#### **User 管理界面**

访问：http://localhost:8000/admin/auth/user/

**增强功能**:
- 列表中显示中文姓名字段
- 可按中文姓名搜索用户
- 快速跳转到 UserProfile 编辑页面

---

### **二、登录页面优化**

访问：http://localhost:8000/login/

**新特性**:
1. ✅ 标签改为"用户名/姓名"
2. ✅ 占位符提示"请输入用户名或真实姓名"
3. ✅ 底部提示信息："支持使用用户名、真实姓名或邮箱登录"

---

## 💡 实际应用场景

### **场景 1: 新员工入职**

**HR 操作流程**:
1. 在 Admin 后台创建用户
   ```
   用户名：zhangsan （自动生成或手动输入）
   密码：123456
   邮箱：zhangsan@company.com
   ```

2. 立即设置中文姓名
   - 方法 A: 在用户编辑页面直接填写"姓名"字段
   - 方法 B: 使用命令行 `python manage.py set_chinese_name --username zhangsan --name "张三"`

3. 告知员工登录方式
   ```
   您可以使用以下方式登录:
   - 用户名：zhangsan
   - 姓名：张三
   - 邮箱：zhangsan@company.com
   初始密码：123456
   ```

---

### **场景 2: 批量导入现有员工**

**管理员操作流程**:

1. **导出当前用户列表**
   - 进入 Admin → Users
   - 导出所有用户名

2. **准备 CSV 文件**
   ```csv
   用户名，中文姓名
   lisi，李四
   wangwu，王五
   zhaoliu，赵六
   sunqi，孙七
   ```

3. **执行批量导入**
   ```bash
   python manage.py set_chinese_name --file employee_names.csv
   ```

4. **验证结果**
   ```
   ✓ 更新：lisi -> 李四
   ✓ 更新：wangwu -> 王五
   ...
   完成！成功：100 条，失败：0 条
   ```

5. **通知全员**
   ```
   各位同事:
   
   系统已升级，现在可以使用中文姓名登录！
   
   登录方式:
   - 姓名 + 密码（推荐）
   - 用户名 + 密码
   - 邮箱 + 密码
   
   请相互转告。
   ```

---

### **场景 3: 忘记用户名怎么办？**

**解决方案**:
1. 在登录页面的用户名框输入中文姓名
2. 例如：`张三`
3. 输入密码
4. 点击登录

系统会自动查找匹配的用户！

---

### **场景 4: 同名同姓怎么办？**

**处理规则**:
如果系统中有多个"张三"，系统会：
1. 优先匹配 username = "zhangsan" 的用户
2. 如果有多个匹配，返回第一个有效用户

**建议**:
- 使用"用户名 + 部门"的方式区分
- 或使用邮箱登录（唯一）

---

## 🔧 技术实现细节

### **认证后端**

文件：[`eims_app/backends.py`](file://e:\EIMS2026\eims_app\backends.py)

**核心类**: `ChineseUsernameAuthenticationBackend`

**认证流程**:
```python
1. 接收登录凭证（username 参数）
   ↓
2. 尝试匹配 User.username 或 User.email
   ↓
3. 如果没找到，尝试匹配 UserProfile.real_name
   ↓
4. 验证密码
   ↓
5. 返回用户对象
```

---

### **数据库结构**

**User 表** (Django 内置):
```
- id (主键)
- username (用户名，可以是中文)
- email (邮箱)
- password (密码)
- is_active (是否激活)
- ...
```

**UserProfile 表** (自定义):
```
- id (主键)
- user_id (外键，关联 User 表)
- real_name (中文姓名) ✨
- gender (性别)
- birthday (生日)
- phone (手机号)
- wechat (微信号)
```

---

### **配置文件**

[`settings.py`](file://e:\EIMS2026\settings.py#L107-L109):
```python
AUTHENTICATION_BACKENDS = [
    'eims_app.backends.ChineseUsernameAuthenticationBackend',
]
```

---

## 📊 数据管理

### **查看已设置的中文姓名**

**方法 1: Admin 后台**
```
http://localhost:8000/admin/eims_app/userprofile/
```

**方法 2: Python Shell**
```bash
python manage.py shell
```

```python
from eims_app.models.model_user import UserProfile

# 查看所有用户的中文姓名
profiles = UserProfile.objects.all()
for p in profiles:
    print(f"{p.user.username}: {p.real_name or '未设置'}")
```

---

### **修改中文姓名**

**方法 1: Admin 后台编辑**

**方法 2: 命令行**
```bash
python manage.py set_chinese_name --username zhangsan --name "李四"
```

**方法 3: Python Shell**
```python
from eims_app.models.model_user import UserProfile

profile = UserProfile.objects.get(user__username='zhangsan')
profile.real_name = '李四'
profile.save()
```

---

### **删除中文姓名**

```python
from eims_app.models.model_user import UserProfile

profile = UserProfile.objects.get(user__username='zhangsan')
profile.real_name = ''
profile.save()
```

之后该用户只能使用用户名或邮箱登录。

---

## ⚠️ 注意事项

### **1. 用户名规范**

虽然支持中文用户名，但建议：
- ✅ **用户名使用拼音**：zhangsan
- ✅ **姓名使用中文**：张三
- ❌ **避免用户名直接用中文**：张三（作为用户名）

**原因**:
- 拼音用户名兼容性更好
- 数据库查询效率更高
- 避免编码问题

---

### **2. 唯一性约束**

- ✅ 用户名必须唯一
- ✅ 邮箱必须唯一
- ❌ **中文姓名可以不唯一**（允许同名同姓）

**影响**:
如果多人同名（如"张三"），系统可能无法准确识别，建议使用用户名或邮箱登录。

---

### **3. 历史数据兼容**

对于已有用户：
- ✅ 不影响原有登录方式
- ✅ 可选择性设置中文姓名
- ✅ 未设置中文姓名的用户仍用用户名登录

---

### **4. 安全性**

- ✅ 密码验证逻辑不变
- ✅ 支持账户锁定功能
- ✅ 支持权限控制

---

## 🎨 界面预览

### **登录页面**

```
┌─────────────────────────────────┐
│   EIMS 工程信息管理系统          │
│   广西晟昌                      │
├─────────────────────────────────┤
│                                 │
│  用户名/姓名                    │
│  ┌─────────────────────────┐   │
│  │ 👤 请输入用户名或真实姓名│   │
│  └─────────────────────────┘   │
│  ℹ 支持使用用户名、真实姓名或邮箱登录│
│                                 │
│  密码                           │
│  ┌─────────────────────────┐   │
│  │ 🔒 请输入密码           │   │
│  └─────────────────────────┘   │
│                                 │
│  [      登  录      ]           │
│                                 │
└─────────────────────────────────┘
```

---

### **Admin 后台 - 用户资料列表**

```
┌──────────────────────────────────────────────┐
│ 用户资料                                     │
├──────────────────────────────────────────────┤
│ [+ 增加] [导出选中的用户资料]                │
├──────────────────────────────────────────────┤
│ 用户名   │ 姓名  │ 性别 │ 电话       │ 微信 │
├──────────┼───────┼──────┼────────────┼──────┤
│ admin    │ 管理员│ 男   │ 138****    │ -    │
│ zhangsan │ 张三  │ 男   │ 139****    │ wx123│
│ lisi     │ 李四  │ 女   │ 137****    │ -    │
└──────────────────────────────────────────────┘
```

---

## 🛠️ 故障排查

### **问题 1: 设置中文姓名后无法登录**

**可能原因**:
- 密码错误
- 账户被禁用（is_active=False）
- 姓名包含空格或特殊字符

**解决方法**:
```python
# 检查用户状态
from django.contrib.auth.models import User

user = User.objects.get(username='zhangsan')
print(f"is_active: {user.is_active}")
print(f"password: {user.password}")

# 重置密码
user.set_password('newpassword123')
user.save()
```

---

### **问题 2: 提示"用户不存在"**

**可能原因**:
- 输入的姓名有误
- 该用户未设置中文姓名

**解决方法**:
1. 确认姓名是否正确（包括大小写、空格）
2. 检查是否已设置 UserProfile:
   ```python
   from eims_app.models.model_user import UserProfile
   
   try:
       profile = UserProfile.objects.get(real_name='张三')
       print(f"找到用户：{profile.user.username}")
   except UserProfile.DoesNotExist:
       print("未找到该用户")
   ```

---

### **问题 3: 批量导入失败**

**可能原因**:
- CSV 文件编码不正确
- 文件格式错误
- 用户名不存在

**解决方法**:
1. 确保 CSV 文件使用 UTF-8 编码
2. 检查 CSV 格式（两列：用户名，中文姓名）
3. 先测试单个用户：
   ```bash
   python manage.py set_chinese_name --username zhangsan --name "张三"
   ```

---

## 📝 最佳实践

### **1. 命名规范**

| 类型 | 推荐格式 | 示例 |
|------|---------|------|
| 用户名 | 小写拼音 | zhangsan, lisi |
| 中文姓名 | 标准汉字 | 张三，李四 |
| 邮箱 | 公司邮箱 | zhangsan@company.com |

---

### **2. 初始化流程**

**新用户入职清单**:
- [ ] 创建 User 账户
- [ ] 设置初始密码
- [ ] 填写 UserProfile（含中文姓名）
- [ ] 分配权限
- [ ] 告知登录方式

---

### **3. 定期维护**

**每月检查**:
- [ ] 清理离职员工账户
- [ ] 更新员工姓名信息
- [ ] 检查同名用户
- [ ] 导出用户资料备份

---

## 📚 相关文件

### **代码文件**
1. [`eims_app/backends.py`](file://e:\EIMS2026\eims_app\backends.py) - 认证后端
2. [`eims_app/admin_user.py`](file://e:\EIMS2026\eims_app\admin_user.py) - Admin 配置
3. [`eims_app/models/model_user.py`](file://e:\EIMS2026\eims_app\models\model_user.py) - UserProfile 模型
4. [`eims_app/management/commands/set_chinese_name.py`](file://e:\EIMS2026\eims_app\management\commands\set_chinese_name.py) - 管理命令

---

### **模板文件**
1. [`eims_app/templates/login.html`](file://e:\EIMS2026\eims_app\templates\login.html) - 登录页面

---

### **配置文件**
1. [`settings.py`](file://e:\EIMS2026\settings.py#L107-L109) - 认证后端配置

---

### **示例文件**
1. [`chinese_names_example.csv`](file://e:\EIMS2026\chinese_names_example.csv) - CSV 示例

---

## 🎉 总结

✅ **已实现功能**:
1. ✅ 支持中文姓名登录
2. ✅ 支持用户名登录（保持兼容）
3. ✅ 支持邮箱登录
4. ✅ Admin 后台可视化管理
5. ✅ 批量导入工具
6. ✅ 完善的提示信息

---

**使用建议**:
- 推荐使用中文姓名登录（更直观）
- 重要操作建议使用用户名或邮箱（避免同名混淆）
- 定期备份用户资料数据

---

**技术支持**: 如有问题，请联系系统管理员。

**更新时间**: 2026-03-25  
**版本**: v1.0
