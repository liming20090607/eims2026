# 项目详情页长文本显示优化

## 🎯 问题描述

**现象**：项目详情页"资金与结算"部分，"项目规模"和"项目地址"字段内容过长时出现文字重叠。

**原因**：
- CSS 使用 `white-space: nowrap` 禁止换行
- `overflow: hidden` 隐藏溢出内容
- 列宽固定，无法根据内容自动调整

---

## ✅ 解决方案

### 1. CSS 样式优化

**文件**：`eims_app/templates/project_ledger/detail.html`

**修改内容**：

```css
/* 字段内容 - 基础样式 */
.field-value {
    font-size: 13px;
    color: #212529;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    word-wrap: break-word;      /* 新增：允许单词内换行 */
    word-break: break-all;      /* 新增：允许任意字符间换行 */
}

/* 特殊字段：允许自动换行（项目规模、项目地址等长文本） */
.field-item.long-text .field-value {
    white-space: normal;        /* 允许换行 */
    line-height: 1.5;           /* 行高 1.5 倍 */
    max-height: 4.5em;          /* 限制最多 3 行 */
    overflow-y: auto;           /* 超出显示滚动条 */
}

/* 为长文本字段增加最小宽度 */
.field-item.long-text {
    min-width: 150px;
}
```

### 2. HTML 模板修改

**修改字段**：
- ✅ 项目规模（第 619 行）
- ✅ 项目地址（第 631 行）

**修改前**：
```html
<div class="field-item">
    <span class="field-label">项目规模:</span>
    <span class="field-value">{{ project_detail.project_scale|default:"-" }}</span>
</div>

<div class="field-item">
    <span class="field-label">项目地址:</span>
    <span class="field-value">{{ project_detail.project_address|default:"-" }}</span>
</div>
```

**修改后**：
```html
<div class="field-item long-text">
    <span class="field-label">项目规模:</span>
    <span class="field-value">{{ project_detail.project_scale|default:"-" }}</span>
</div>

<div class="field-item long-text">
    <span class="field-label">项目地址:</span>
    <span class="field-value">{{ project_detail.project_address|default:"-" }}</span>
</div>
```

---

## 🎨 效果对比

### 修改前
```
┌─────────────────────────────────────┐
│ 项目规模：                           │
│ 1#、3#、5#楼及地下室，总建筑面积 495 │ ← 文字重叠被截断
│ 项目地址：                           │
│ 桂林市雁山区雁中路以北，雁山科教园 │ ← 文字重叠被截断
└─────────────────────────────────────┘
```

### 修改后
```
┌─────────────────────────────────────┐
│ 项目规模：                           │
│ 1#、3#、5#楼及地下室，总建筑面积     │
│ 49522.71 平方米 (其中总计容建筑面    │ ← 自动换行，完整显示
│ 积 34350 平方米，不计容建筑面积：    │
│ 11712.71 平方米)                     │
│ 项目地址：                           │
│ 桂林市雁山区雁中路以北，雁山科教园 │ ← 自动换行，完整显示
│ 区路以东                             │
└─────────────────────────────────────┘
```

---

## 📊 技术细节

### 1. 列宽自动调整原理

**CSS Grid 布局**：
```css
.field-grid-sub {
    display: grid !important;
    grid-template-columns: repeat(12, 1fr) !important;
    gap: 4px;
    width: 100%;
}
```

**字段项弹性布局**：
```css
.field-item {
    display: flex;
    flex-direction: column;
    min-width: 0;      /* 允许缩小 */
    padding: 3px;
    background: white;
    border-radius: 3px;
    border: 1px solid #dee2e6;
}

.field-item.long-text {
    min-width: 150px;  /* 长文本字段最小宽度 */
}
```

### 2. 文字换行机制

**三种换行方式**：
1. `white-space: normal` - 正常换行（空格、标点处）
2. `word-wrap: break-word` - 单词内换行（长单词自动断行）
3. `word-break: break-all` - 任意字符间换行（中文专用）

**组合使用**：
```css
white-space: normal;      /* 允许正常换行 */
word-wrap: break-word;    /* 长单词自动断行 */
word-break: break-all;    /* 中文任意换行 */
```

### 3. 高度限制与滚动

**限制最多 3 行**：
```css
max-height: 4.5em;        /* 1.5em × 3 行 = 4.5em */
line-height: 1.5;         /* 行高 1.5 倍 */
overflow-y: auto;         /* 超出显示垂直滚动条 */
```

**计算方式**：
- 字体大小：13px
- 行高：1.5 × 13px = 19.5px
- 3 行高度：3 × 19.5px = 58.5px ≈ 4.5em

---

## 🔧 其他长文本字段

如果其他字段也需要同样处理，只需两步：

### 步骤 1：添加 CSS 类
```html
<div class="field-item long-text">
    <span class="field-label">字段名:</span>
    <span class="field-value">长文本内容</span>
</div>
```

### 步骤 2：无需额外 CSS
样式已自动应用，因为 `.field-item.long-text` 的 CSS 已定义。

**适用字段**：
- ✅ 备注（如需显示完整内容）
- ✅ 合同约定
- ✅ 技术规范
- ✅ 其他长文本字段

---

## 📝 响应式布局

### 不同屏幕尺寸下的表现

**大屏幕（>1200px）**：
- 12 列网格
- 每个字段占 1 列（8.33%）
- 长文本字段自动换行

**中等屏幕（768px-1200px）**：
- 8 列网格
- 每个字段占 1 列（12.5%）
- 长文本字段换行更频繁

**小屏幕（<768px）**：
- 6 列网格
- 每个字段占 1 列（16.67%）
- 长文本字段充分换行

---

## 🎯 用户体验提升

### 1. 可读性
- ✅ 文字不再重叠
- ✅ 内容完整显示
- ✅ 支持滚动查看

### 2. 美观性
- ✅ 自动换行整齐
- ✅ 行间距适中
- ✅ 最大高度限制

### 3. 实用性
- ✅ 短文本保持单行
- ✅ 长文本自动换行
- ✅ 超长按滚动显示

---

## 🔍 测试验证

### 测试场景

**场景 1：短文本（<20 字）**
```
项目规模：3 栋楼
项目地址：北京市朝阳区
```
**预期**：单行显示，不换行

**场景 2：中等文本（20-50 字）**
```
项目规模：1#、3#楼及地下室，总建筑面积 49522.71 平方米
项目地址：桂林市雁山区雁中路以北，雁山科教园区
```
**预期**：2-3 行，自动换行

**场景 3：长文本（>50 字）**
```
项目规模：1#、3#、5#楼及地下室，总建筑面积 49522.71 平方米 (其中总计容建筑面积 34350 平方米，不计容建筑面积：11712.71 平方米)
项目地址：桂林市雁山区雁中路以北，雁山科教园区路以东，雁山大道以西
```
**预期**：3 行 + 滚动条

---

## 📋 文件清单

### 修改的文件
- ✅ `eims_app/templates/project_ledger/detail.html`

### 修改位置
- CSS 样式：第 262-285 行
- HTML 模板：第 619 行、第 631 行

---

## 🎓 最佳实践

### 1. 字段分类
- **短文本字段**：金额、日期、状态 → 保持单行
- **中长文本字段**：规模、地址 → 自动换行
- **超长文本字段**：备注、说明 → 滚动显示

### 2. 高度控制
- **3 行以内**：直接显示（`max-height: 4.5em`）
- **超过 3 行**：滚动显示（`overflow-y: auto`）
- **重要信息**：避免隐藏（不使用 `overflow: hidden`）

### 3. 响应式考虑
- **桌面端**：充分利用宽度
- **移动端**：优先保证可读性
- **平板端**：平衡宽度与换行

---

## 📞 维护建议

### 1. 定期检查
- 检查长文本字段显示效果
- 验证滚动条功能正常
- 确认响应式布局正确

### 2. 新增字段
- 评估字段内容长度
- 决定是否添加 `long-text` 类
- 测试不同屏幕尺寸效果

### 3. 样式调整
- 如需修改最大高度，调整 `max-height`
- 如需修改行间距，调整 `line-height`
- 如需修改最小宽度，调整 `min-width`

---

**文档版本**: 1.0  
**创建时间**: 2026-03-28  
**适用系统**: EIMS2026
