# 合同管理与项目台账数据导入方案

## 📊 **当前问题分析**

### **问题描述**
用户发现：
- 在合同管理页面导入的数据，在项目台账看不到
- 在项目台账导入的数据，在合同管理看不到
- 两边数据不一致

### **根本原因**

```
❌ 当前状态：
合同管理模块 → 没有导入功能
项目台账模块 → 没有导入功能
项目管理模块 → 有导入功能，但导入到旧的 Project 表

✅ 应该的状态：
合同管理模块 → 导入到 ProjectDetail 表
项目台账模块 → 导入到 ProjectDetail 表
项目管理模块 → 导入到旧的 Project 表（向后兼容）
```

### **数据模型关系**

```
旧架构：
Project 表 ← 项目管理模块使用
Contract 表 ← 合同管理模块使用（旧）

新架构（单表多视图）：
ProjectDetail 表 ← 项目台账模块使用
                ← 合同管理模块使用
                ← 两者数据实时同步
```

---

## ✅ **解决方案**

### **方案 A：为两个模块分别创建导入功能（推荐）**

**优点**：
- ✅ 每个模块独立导入
- ✅ 导入字段可定制
- ✅ 用户体验好
- ✅ 符合单表多视图架构

**实施步骤**：

#### **1. 创建项目台账导入视图**

文件：`views_project_ledger.py`

功能：
- 导入到 `ProjectDetail` 表
- 支持 Excel 导入
- 字段映射：项目台账的 28 个字段

#### **2. 创建合同管理导入视图**

文件：`views_contract_management.py`

功能：
- 导入到 `ProjectDetail` 表
- 支持 Excel 导入
- 字段映射：合同管理的 22 个字段

#### **3. 创建导入模板**

- 项目台账导入模板.xlsx
- 合同管理导入模板.xlsx

#### **4. 创建导入页面**

- `templates/project_ledger/import.html`
- `templates/contract_management/import.html`

---

### **方案 B：统一导入到 ProjectDetail（简化版）**

**优点**：
- ✅ 实现简单
- ✅ 快速解决问题
- ✅ 数据统一

**实施**：
在两个模块的列表页面添加"导入"按钮，跳转到统一的导入页面。

---

## 🎯 **推荐实施方案 A**

### **实施计划**

#### **阶段 1：创建项目台账导入功能**

**步骤**：
1. 创建导入视图函数
2. 创建导入表单
3. 创建导入模板
4. 创建导入页面
5. 配置 URL

**字段映射（28 个）**：
```python
# 必填字段
project_code          # 项目编号
contract_code         # 合同编号
project_name          # 项目名称
contract_party_a      # 合同甲方
contract_party_b      # 合同乙方
signing_date          # 签订日期
contract_amount       # 合同总价

# 可选字段
monthly_report_required      # 项目月报
project_status               # 项目状态
contract_status              # 合同状态
payment_agreement            # 付款约定
project_scale                # 项目规模
project_investment           # 项目总投资
project_address              # 项目地址
service_period               # 服务周期
service_deadline             # 服务到期日期
extension_agreement          # 延期约定
actual_extension_status      # 实际延期情况
construction_permit_status   # 施工许可证状态
entry_notice                 # 进场通知
entry_time                   # 进场时间
actual_start_date            # 实际开工日期
estimated_completion_date    # 预计竣工日期
project_director             # 项目总监
project_manager              # 现场负责人
contact_phone                # 联系电话
remark                       # 备注
```

---

#### **阶段 2：创建合同管理导入功能**

**步骤**：
1. 创建导入视图函数
2. 创建导入表单
3. 创建导入模板
4. 创建导入页面
5. 配置 URL

**字段映射（22 个）**：
```python
# 必填字段
contract_category     # 合同类别
contract_code         # 合同编号
project_name          # 项目名称
contract_party_a      # 合同甲方
contract_party_b      # 合同乙方
signing_date          # 签订日期
contract_amount       # 合同总价

# 可选字段
contract_status              # 合同状态
settlement_status            # 结算情况
payment_agreement            # 付款约定
project_scale                # 项目规模
project_investment           # 项目总投资
project_address              # 项目地址
agreed_staffing              # 约定人员配备
service_period               # 服务周期
service_deadline             # 服务到期日期
extension_agreement          # 延期约定
planned_start_date           # 计划开工日期
estimated_completion_date    # 预计竣工日期
remark                       # 备注
```

---

## 📝 **数据一致性保证**

### **导入后的数据同步**

```python
# 无论在哪个模块导入，数据都存储在 ProjectDetail 表

# 项目台账导入
ProjectDetail.objects.create(
    project_code='XM2026001',
    contract_code='HT2026001',
    project_name='测试项目',
    # ... 其他字段
)

# 合同管理导入
ProjectDetail.objects.create(
    contract_category='engineering_supervision',
    contract_code='HT2026002',
    project_name='测试合同',
    # ... 其他字段
)

# 两个模块查询的都是同一个表
ProjectDetail.objects.all()  # 两边都能看到
```

### **验证数据同步**

```
测试步骤：
1. 在项目台账导入项目 A
2. 访问合同管理列表
   ✅ 应该能看到项目 A

3. 在合同管理导入合同 B
4. 访问项目台账列表
   ✅ 应该能看到合同 B

5. 在项目台账修改项目 A 的现场负责人
6. 在合同管理查看详情
   ✅ 现场负责人应该是新值
```

---

## 🚀 **立即解决方案**

### **临时方案（无需编码）**

如果急需导入数据，可以：

1. **直接在 Django Admin 后台导入**
   ```
   访问：http://localhost:8000/admin/
   登录管理员账号
   进入 ProjectDetail 表
   使用 Django 的导入功能
   ```

2. **使用数据库工具直接导入**
   ```
   使用 Navicat、DBeaver 等工具
   直接插入到 eims_app_projectdetail 表
   ```

3. **使用 Python 脚本批量导入**
   ```python
   # import_data.py
   import pandas as pd
   from eims_app.models import ProjectDetail
   
   df = pd.read_excel('data.xlsx')
   for index, row in df.iterrows():
       ProjectDetail.objects.create(
           project_code=row['项目编号'],
           contract_code=row['合同编号'],
           project_name=row['项目名称'],
           # ... 其他字段
       )
   ```

---

## ⚠️ **注意事项**

### **1. 字段验证**
- 必填字段必须填写
- 字段格式验证（日期、数字等）
- 唯一性验证（项目编号等）

### **2. 数据清洗**
- 去除空格
- 统一格式
- 处理空值

### **3. 错误处理**
- 导入失败提示
- 错误行定位
- 部分成功处理

### **4. 权限控制**
- 只有管理员可以导入
- 导入前备份数据
- 导入日志记录

---

## 📞 **下一步行动**

请告诉我您希望：

**选项 A**：完整实施两个模块的导入功能（推荐）
- 我会创建所有必要的代码
- 预计需要 30-40 分钟
- 用户体验最佳

**选项 B**：简化版统一导入
- 快速实现
- 共用导入页面
- 预计需要 15-20 分钟

**选项 C**：临时方案
- 先使用 Django Admin 导入
- 后续再完善功能

我会根据您的选择立即开始实施！🚀

---

**当前状态**：
- ✅ 单表多视图架构已建立
- ✅ 项目台账和合同管理都使用 ProjectDetail 表
- ❌ 两个模块都没有导入功能
- ❌ 旧项目管理模块导入到错误的表

**解决后**：
- ✅ 两个模块都有独立的导入功能
- ✅ 都导入到 ProjectDetail 表
- ✅ 数据实时同步
- ✅ 用户体验统一
