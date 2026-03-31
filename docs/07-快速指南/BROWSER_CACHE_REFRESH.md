# 浏览器缓存刷新说明

## 问题原因
修改 CSS 样式后，浏览器可能仍然使用缓存的旧样式文件，导致新布局不生效。

## 解决方案

### 方法 1：强制刷新（推荐）
**Windows 系统：**
- 按 `Ctrl + Shift + R`
- 或按 `Ctrl + F5`

**Mac 系统：**
- 按 `Cmd + Shift + R`

### 方法 2：清除浏览器缓存
**Chrome/Edge：**
1. 按 `F12` 打开开发者工具
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

**Firefox：**
1. 按 `Ctrl + Shift + Delete`
2. 勾选"缓存"
3. 点击"立即清除"

### 方法 3：无痕模式测试
1. 按 `Ctrl + Shift + N` (Chrome/Edge) 或 `Ctrl + Shift + P` (Firefox)
2. 打开无痕窗口
3. 重新访问页面

## 验证方法
刷新页面后，检查以下变化：
- ✅ 项目基本信息组应该是 2 列并排显示
- ✅ 资金与结算组应该是 3 列并排显示
- ✅ 服务周期与进度组应该是 3 列并排显示
- ✅ 人员与文档组应该是 2 列并排显示
- ✅ 右侧不应该有大面积空白

## 如果仍然不生效
1. 检查是否按了正确的强制刷新快捷键
2. 尝试关闭所有浏览器窗口后重新打开
3. 检查服务器是否已重启（虽然 CSS 修改通常不需要重启服务器）

## 技术说明
已在模板中添加了 `!important` 标记来强制应用 CSS Grid 布局：
```css
.info-grid-main {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
}

.info-grid-sub {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
}
```
