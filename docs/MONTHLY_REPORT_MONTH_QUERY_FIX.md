# 月度报告月份查询 Bug 修复

## 问题描述

用户填报了燕林学府项目的月报后，在待填报项目列表中仍然显示该项目需要填报。

## 根本原因

**数据格式不匹配**：

1. **数据库存储格式**：`MonthlyReport.report_month` 字段是 `CharField`，存储为 `"YYYY-MM"` 格式（如 `"2026-03"`）

2. **查询使用格式**：代码中使用数字月份（如 `3`）进行查询

3. **结果**：字符串 `"2026-03"` ≠ 数字 `3`，导致查询不到已填报的记录

## 问题代码位置

### 1. `views_monthly_report.py` - `monthly_report_dashboard()`

**错误代码**（第 295-299 行）：
```python
existing_report = MonthlyReport.objects.filter(
    project=project,
    report_year=current_year,
    report_month=current_month_num  # ❌ 使用数字 3
).first()
```

**修复后**：
```python
# 当前月份的字符串格式（用于查询）
current_month_str = f"{current_year}-{current_month_num:02d}"  # 格式：YYYY-MM

existing_report = MonthlyReport.objects.filter(
    project=project,
    report_year=current_year,
    report_month=current_month_str  # ✅ 使用字符串 "2026-03"
).first()
```

### 2. `views_monthly_report.py` - `monthly_report_list()`

**错误代码**（第 40-41 行）：
```python
if report_month:
    year, month = map(int, report_month.split('-'))
    reports = reports.filter(report_year=year, report_month=month)  # ❌ 使用数字
```

**修复后**：
```python
if report_month:
    # report_month 是字符串格式 "YYYY-MM"，直接使用
    reports = reports.filter(report_month=report_month)  # ✅ 直接使用字符串
```

### 3. `form_monthly_report.py` - `MonthlyReportForm.__init__()`

**错误代码**（第 207-211 行）：
```python
last_month_report = MonthlyReport.objects.filter(
    project=initial_project,
    report_year=last_month.year,
    report_month=last_month.month  # ❌ 使用数字
).first()
```

**修复后**：
```python
# 使用字符串格式的月份
last_month_str = f"{last_month.year}-{last_month.month:02d}"
last_month_report = MonthlyReport.objects.filter(
    project=initial_project,
    report_year=last_month.year,
    report_month=last_month_str  # ✅ 使用字符串 "2026-02"
).first()
```

### 4. `model_user.py` - `MonthlyReport.save()`

**错误代码**（第 182 行）：
```python
self.should_submit_date = date(self.report_year, self.report_month, 25)  # ❌ report_month 是字符串
```

**修复后**：
```python
# report_month 是字符串格式 "YYYY-MM"，需要解析
if self.report_month and '-' in str(self.report_month):
    year, month = map(int, self.report_month.split('-'))
    self.should_submit_date = date(year, month, 25)  # ✅ 解析后使用
else:
    # 如果是数字或其他格式，直接作为月份
    self.should_submit_date = date(self.report_year, int(self.report_month), 25)
```

## 修复文件清单

1. ✅ `eims_app/views/views_monthly_report.py`
   - 修复 `monthly_report_dashboard()` 函数
   - 修复 `monthly_report_list()` 函数

2. ✅ `eims_app/forms/form_monthly_report.py`
   - 修复 `MonthlyReportForm.__init__()` 方法

3. ✅ `eims_app/models/model_user.py`
   - 修复 `MonthlyReport.save()` 方法

## 测试验证

### 测试脚本
- `test_monthly_report_month_fix.py` - 验证月份查询格式
- `create_test_report.py` - 创建测试数据

### 测试结果
```
当前日期：2026-03-28
当前年份：2026
当前月份（数字）：3
当前月份（字符串）：2026-03

【测试 1】使用字符串格式查询：report_month='2026-03'
  ✓ 找到 1 条记录

【测试 2】使用数字格式查询：report_month=3
  ✓ 正确！数字格式找不到任何记录

【测试 3】模拟 dashboard 待填报列表查询
  ✓ 燕林学府：已填报 (2026-03)
```

## 最佳实践建议

### 1. **日期字段设计规范**
- ✅ **CharField 存储日期**：使用 `"YYYY-MM"` 格式（如 `"2026-03"`）
- ✅ **优点**：
  - 便于显示和排序
  - 避免时区问题
  - 支持模糊查询（如 `report_month__startswith='2026'`）

### 2. **查询一致性原则**
- ⚠️ **查询格式必须与存储格式一致**
- ❌ 不要混用字符串和数字
- ✅ 使用相同格式：`report_month='2026-03'`

### 3. **日期字段辅助方法**
```python
# 推荐：在模型中添加辅助方法
class MonthlyReport(models.Model):
    report_month = models.CharField(max_length=7, ...)
    
    @property
    def get_report_month_tuple(self):
        """返回 (year, month) 元组"""
        if '-' in self.report_month:
            return map(int, self.report_month.split('-'))
        return None
    
    @property
    def get_report_month_date(self):
        """返回 date 对象"""
        year, month = self.get_report_month_tuple
        return date(year, month, 1)
```

## 影响范围

- ✅ **待填报列表**：正确显示已填报项目
- ✅ **月度报告筛选**：正确按月份筛选
- ✅ **表单初始化**：正确获取上月数据
- ✅ **应提交日期计算**：正确解析月份设置截止日期

## 总结

**核心问题**：数据类型不匹配（字符串 vs 数字）

**解决方案**：统一使用字符串格式 `"YYYY-MM"` 进行查询和存储

**关键要点**：
1. 始终检查字段类型（CharField vs IntegerField）
2. 查询格式必须与存储格式一致
3. 日期字符串需要解析后才能用于日期构造函数

---

**修复日期**：2026-03-28  
**修复人员**：AI Assistant  
**测试状态**：✅ 已通过
