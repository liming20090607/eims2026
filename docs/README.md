# 协同 AI 办公系统 (AOS) - 项目文档索引

## 📁 文档目录结构

```
docs/
├── 01-项目文档/          # 项目整体文档、需求分析、系统架构
├── 02-功能说明/          # 各功能模块详细说明
├── 03-部署指南/          # 服务器部署、环境配置
├── 04-问题修复/          # Bug 修复记录
├── 05-优化记录/          # 性能优化、UI 优化记录
├── 06-测试调试/          # 测试脚本、调试工具
└── 07-快速指南/          # 快速入门、使用指南
```

---

## 📂 分类说明

### 01-项目文档
存放项目整体相关文档：
- 项目分析报告
- 系统架构设计
- 数据库设计文档
- 需求规格说明

**包含文件：**
- `OA_SYSTEM_ANALYSIS.md` - OA 系统分析报告
- `DATABASE_RECONSTRUCTION_FINAL_REPORT.md` - 数据库重构最终报告
- `DETAILED_IMPLEMENTATION_PLAN.md` - 详细实施计划

---

### 02-功能说明
各功能模块的详细说明文档：

**人员管理模块：**
- `PERSONNEL_MODULE_GUIDE.md`
- `PERSONNEL_QUICK_START.md`
- `CHINESE_USERNAME_LOGIN_GUIDE.md`
- `一人多项目功能实现说明.md`

**项目管理模块：**
- `PROJECT_DETAIL_PAGE_CREATED.md`
- `PROJECT_DETAIL_MAIN_SUB_PANELS.md`
- `SIDEBAR_PROJECT_DETAIL_FEATURE.md`

**合同管理模块：**
- `CONTRACT_LEDGER_FIELDS_OPTIMIZATION.md`
- `CONTRACT_SUBMENU_FEATURE.md`
- `PROJECT_CONTRACT_RESTRUCTURE_SUMMARY.md`

**审批流程模块：**
- `CONTRACT_APPROVAL_WORKFLOW_IMPLEMENTATION.md`
- `CONTRACT_APPROVAL_SYSTEM_COMPLETE.md`
- `部门管理与审批流程增强_使用说明.md`

**文档管理模块：**
- `IMPORT_EXPORT_FEATURE_COMPLETE.md`
- `IMPORT_TEMPLATE_FEATURE.md`

**月度报表模块：**
- `MONTHLY_REPORT_FORM_UPGRADE.md`
- `MONTHLY_REPORT_SYNC_FEATURE.md`

**可视化分配：**
- `可视化人员分配功能说明.md`
- `可视化人员分配_快速上手.md`

---

### 03-部署指南
服务器部署和环境配置相关：

**阿里云部署：**
- `ALIYUN_DEPLOYMENT_GUIDE.md`
- `ALIYUN_ECS_ANALYSIS.md`
- `QUICK_START_ALIYUN.md`

**自建服务器：**
- `SELF_HOSTED_SERVER_GUIDE.md`
- `SERVER_REQUIREMENTS.md`

**生产环境配置：**
- `Production Server and Security Configuration.md`
- `MULTI_SYSTEM_DEPLOYMENT.md` - 多系统共存部署

**部署检查清单：**
- `DEPLOYMENT_CHECKLIST.md`
- `QUICK_DEPLOY.md`

---

### 04-问题修复
Bug 修复记录和技术问题解决方案：

**URL 和路由问题：**
- `FIX_NO_REVERSE_MATCH_PROJECT_VIEW.md`
- `NAMESPACE_URL_FIX.md`
- `URL_ROUTE_FIX.md`
- `CORRECT_URL_FORMAT.md`

**CSRF 问题：**
- `CSRF_ERROR_SOLUTION.md`
- `CSRF_FIX.md`
- `CSRF_BATCH_DELETE_FIX.md`

**数据库问题：**
- `DATABASE_CLEANUP_*` 系列文档
- `CONTRACT_TABLE_IS_DELETED_FIX.md`
- `PROJECT_MODEL_IMPORT_FIX.md`

**前端显示问题：**
- `DATATABLES_*` 系列文档
- `PERSONNEL_DISPLAY_EMPTY_FIX.md`
- `DETAIL_PANEL_TROUBLESHOOTING.md`

**中文姓名问题：**
- `CHINESE_USERNAME_IMPLEMENTATION_SUMMARY.md`
- `MANAGE_USER_NAMES.py`

---

### 05-优化记录
性能优化和 UI/UX改进记录：

**布局优化：**
- `COMPACT_LAYOUT_OPTIMIZATION.md` - 紧凑布局优化
- `SIMPLE_LAYOUT_OPTIMIZATION.md` - 简单布局优化
- `FULL_WIDTH_LIST_LAYOUT.md` - 全宽列表布局
- `TABLE_AUTO_WIDTH_STYLE.md` - 表格自适应宽度

**字体和样式优化：**
- `FONT_SIZE_UPDATE_13PX.md`
- `COMPACT_BUTTON_OPTIMIZATION.md` - 紧凑按钮优化

**字段优化：**
- `CONTRACT_LEDGER_FIELDS_OPTIMIZATION.md`
- `PROJECT_MANAGER_FIELD_REPLACEMENT.md`

**性能优化：**
- `DECIMAL_PRECISION_GUARANTEE.md` - 小数精度保证

---

### 06-测试调试
测试脚本和调试工具相关：

**测试脚本：**
- `run_comprehensive_tests.py` - 综合测试运行器
- `test_chinese_login.py` - 中文登录测试
- `test_personnel.py` - 人员管理测试
- `test_workflow.py` - 工作流测试

**调试工具：**
- `DEBUG_TOOL_GUIDE.md` - 调试工具使用指南
- `DEBUG_TOOL_ENHANCED.md` - 增强版调试工具
- `深度诊断工具说明.md`
- `调试工具快速访问.md`

**数据检查：**
- `check_urls.py` - URL 检查
- `check_pagination.py` - 分页检查
- `verify_personnel.py` - 人员数据验证

---

### 07-快速指南
快速入门和使用指南：

**系统级指南：**
- `WORKFLOW_GUIDE.md` - 工作流指南
- `功能完成总结.md` - 功能完成总结

**模块级指南：**
- `人员管理模块_快速访问指南.md`
- `部门管理系统_快速访问指南.md`
- `PERSONNEL_QUICK_START.md`

**特定功能指南：**
- `一键部署详细说明.md`
- `强制刷新浏览器缓存的方法.md`
- `导入模板下载说明.md`

**权限管理指南：**
- `侧边栏菜单权限管理_使用说明.md`
- `系统导航权限管理_使用说明.md`

---

## 🔧 最近更新的文档

### 项目详情页优化系列
1. `PROJECT_DETAIL_LAYOUT_OPTIMIZATION.md` - 初始布局优化
2. `BROWSER_CACHE_REFRESH.md` - 浏览器缓存刷新指南
3. `COMPACT_LAYOUT_OPTIMIZATION.md` - 紧凑布局优化
4. `SIMPLE_LAYOUT_OPTIMIZATION.md` - 简单布局优化（最新版）

**优化演进过程：**
- 第 1 版：卡片分组 +2 列/3 列布局 → 字体 13px
- 第 2 版：紧凑优化 → 减小间距和字体
- 第 3 版：放大字体 → 26px 大字体
- 第 4 版：简化布局 → inline 排列 +15px 字体（当前版本）

---

## 📝 文档命名规范

### 中文文档
- 使用下划线分隔：`功能名称_说明类型.md`
- 示例：`人员管理模块_快速访问指南.md`

### 英文文档
- 使用下划线和大写：`FEATURE_TYPE_DESCRIPTION.md`
- 示例：`CONTRACT_LEDGER_FIELDS_OPTIMIZATION.md`

---

## 🎯 快速查找指南

**按功能查找：**
- 人员管理 → `02-功能说明/` 搜索 "PERSONNEL" 或 "人员"
- 项目管理 → `02-功能说明/` 搜索 "PROJECT" 或 "项目"
- 合同管理 → `02-功能说明/` 搜索 "CONTRACT" 或 "合同"
- 审批流程 → `02-功能说明/` 搜索 "APPROVAL" 或 "审批"

**按问题查找：**
- URL 错误 → `04-问题修复/` 搜索 "URL" 或 "ROUTE"
- 数据库错误 → `04-问题修复/` 搜索 "DATABASE" 或 "DB"
- 前端显示 → `04-问题修复/` 搜索 "DATATABLES" 或 "DISPLAY"
- CSRF 错误 → `04-问题修复/` 搜索 "CSRF"

**按优化查找：**
- 布局优化 → `05-优化记录/` 搜索 "LAYOUT" 或 "布局"
- 样式优化 → `05-优化记录/` 搜索 "STYLE" 或 "样式"
- 性能优化 → `05-优化记录/` 搜索 "PERFORMANCE" 或 "性能"

---

## 📦 文档维护建议

1. **及时归档**：新功能完成后立即创建文档并归类
2. **版本控制**：重大更新保留历史版本文档
3. **索引更新**：定期更新本索引文件
4. **清理过时**：删除或标记过时的文档

---

## 📅 文档整理日期

最后整理时间：2026 年 3 月 26 日
