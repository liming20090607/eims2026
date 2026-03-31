# 月度报告自动提醒功能实现说明

## 功能概述

在每月最后 5 天，用户登录系统后会自动弹出提醒窗口，提示该用户填报与其相关的"XX 项目"的月度报告。在完成填报之前，每隔 10 分钟弹出一次提醒，完成填报后不再弹窗。

## 核心特性

✅ **智能检测**：自动判断是否为每月最后 5 天  
✅ **精准推送**：只提醒用户负责且需要填报的项目  
✅ **循环提醒**：每 10 分钟提醒一次，直到完成填报  
✅ **一键跳转**：点击"立即填报"直接跳转到项目详情  
✅ **状态同步**：完成填报后自动停止提醒  

## 技术实现

### 1. 中间件层

**文件**: `eims_app/middleware/monthly_report_reminder.py`

#### 主要函数：

**`is_last_five_days_of_month()`**
```python
def is_last_five_days_of_month():
    """判断当前是否为每月最后 5 天"""
    today = date.today()
    # 计算当月最后一天
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    
    last_day_of_month = next_month - timedelta(days=1)
    # 最后 5 天：倒数第 5 天到最后一天
    return last_day_of_month.day - today.day <= 4
```

**`get_pending_reports_for_user(user)`**
```python
def get_pending_reports_for_user(user):
    """获取用户需要填报但还未填报的月度报告项目"""
    # 查询用户负责的所有项目（且需要填报月报）
    reporter_relations = ProjectReporter.objects.filter(
        user=user,
        is_active=True,
        project__monthly_report_required=True
    ).select_related('project')
    
    pending_projects = []
    for relation in reporter_relations:
        project = relation.project
        
        # 检查是否已有当月的月度报告（排除草稿）
        existing_report = MonthlyReport.objects.filter(
            project=project,
            report_year=today.year,
            report_month=f"{today.year}-{today.month:02d}",
            reporter=user
        ).exclude(status='draft').first()
        
        if not existing_report:
            pending_projects.append({
                'project_id': project.id,
                'project_code': project.project_code,
                'project_name': project.project_name,
            })
    
    return pending_projects
```

**`monthly_report_reminder_middleware(get_response)`**
```python
def monthly_report_reminder_middleware(get_response):
    """月度报告提醒中间件"""
    def middleware(request):
        if request.user.is_authenticated:
            if is_last_five_days_of_month():
                pending_projects = get_pending_reports_for_user(request.user)
                
                if pending_projects:
                    request.session['monthly_report_reminder'] = {
                        'pending_projects': pending_projects,
                        'is_last_five_days': True,
                    }
                else:
                    # 清除提醒
                    if 'monthly_report_reminder' in request.session:
                        del request.session['monthly_report_reminder']
            else:
                # 不是最后 5 天，清除提醒
                if 'monthly_report_reminder' in request.session:
                    del request.session['monthly_report_reminder']
        
        response = get_response(request)
        return response
    
    return middleware
```

### 2. API 视图层

**文件**: `eims_app/views/views_monthly_report.py`

#### API 端点：

**`get_pending_reports(request)`** - 获取待填报项目
```python
@login_required
def get_pending_reports(request):
    """获取用户待填报的月度报告项目（API）"""
    # 检查是否为每月最后 5 天
    today = date.today()
    last_day_of_month = ...
    is_last_five_days = (last_day_of_month.day - today.day) <= 4
    
    if not is_last_five_days:
        return JsonResponse({
            'success': True,
            'is_last_five_days': False,
            'pending_projects': [],
            'message': '当前不是每月最后 5 天'
        })
    
    # 查询待填报项目
    reporter_relations = ProjectReporter.objects.filter(
        user=request.user,
        is_active=True,
        project__monthly_report_required=True
    ).select_related('project')
    
    pending_projects = []
    for relation in reporter_relations:
        project = relation.project
        # 检查是否已填报
        existing_report = MonthlyReport.objects.filter(...).exclude(status='draft').first()
        
        if not existing_report:
            pending_projects.append({
                'project_id': project.id,
                'project_code': project.project_code,
                'project_name': project.project_name,
                'detail_url': reverse('eims_app:project_ledger_detail', kwargs={'pk': project.id})
            })
    
    return JsonResponse({
        'success': True,
        'is_last_five_days': True,
        'pending_projects': pending_projects,
        'count': len(pending_projects),
    })
```

**`clear_reminder(request)`** - 清除提醒标记
```python
@login_required
def clear_reminder(request):
    """清除提醒标记（当用户完成填报后调用）"""
    if 'monthly_report_reminder' in request.session:
        del request.session['monthly_report_reminder']
    
    return JsonResponse({'success': True})
```

### 3. 前端展示层

**文件**: `eims_app/templates/base/base.html`

#### JavaScript 逻辑：

**定时检查机制**
```javascript
let reminderInterval = null;
let lastReminderTime = null;

// 页面加载时检查
$(document).ready(function() {
    setTimeout(() => {
        checkMonthlyReportReminder();
    }, 2000); // 延迟 2 秒，避免干扰页面加载
});

// 定期检查（每 10 分钟）
function checkAndShowReminder() {
    const now = new Date().getTime();
    
    // 如果距离上次提醒不到 10 分钟，不显示
    if (lastReminderTime && now - lastReminderTime < 600000) {
        return;
    }
    
    checkMonthlyReportReminder();
}
```

**调用 API 并显示弹窗**
```javascript
function checkMonthlyReportReminder() {
    fetch('/api/monthly-report/pending/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.is_last_five_days && data.pending_projects.length > 0) {
                showMonthlyReportModal(data.pending_projects);
                
                // 设置 10 分钟定时器
                if (reminderInterval) {
                    clearInterval(reminderInterval);
                }
                reminderInterval = setInterval(() => {
                    checkAndShowReminder();
                }, 600000); // 10 分钟
            }
        });
}
```

**模态框展示**
```javascript
function showMonthlyReportModal(pendingProjects) {
    const modalHtml = `
        <div class="modal fade" id="monthlyReportModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle-fill"></i>
                            月度报告填报提醒
                        </h5>
                    </div>
                    <div class="modal-body">
                        <p>您还有 <strong>${pendingProjects.length}</strong> 个项目需要填报</p>
                        <ul class="list-group">
                            ${pendingProjects.map(p => `
                                <li class="list-group-item">
                                    <strong>${p.project_code}</strong><br>
                                    <small>${p.project_name}</small>
                                    <a href="${p.detail_url}" class="btn btn-sm btn-primary">
                                        <i class="bi bi-pencil-square"></i> 立即填报
                                    </a>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary">稍后处理</button>
                        <a href="/monthly-report/dashboard/" class="btn btn-primary">前往填报</a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modalHtml);
    $('#monthlyReportModal').modal({
        backdrop: 'static',
        keyboard: false
    });
    
    lastReminderTime = new Date().getTime();
    
    // 关闭时清理
    $('#monthlyReportModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}
```

## 路由配置

**文件**: `eims_app/urls.py`

```python
# 月度报告提醒 API
path('api/monthly-report/pending/', get_pending_reports, name='get_pending_reports'),
path('api/monthly-report/clear-reminder/', clear_reminder, name='clear_reminder'),
```

## 中间件注册

**文件**: `settings.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'eims_app.middleware.login_required.login_required_middleware',
    'eims_app.middleware.monthly_report_reminder.monthly_report_reminder_middleware',  # 新增
]
```

## 使用流程

### 场景 1：每月最后 5 天登录

```
1. 用户登录系统
   ↓
2. 中间件检测到是每月最后 5 天
   ↓
3. 查询用户是否有待填报的项目
   ↓
4. 如果有 → 在 session 中存储提醒信息
   ↓
5. 页面加载 2 秒后，JavaScript 调用 API
   ↓
6. 显示提醒弹窗，列出所有待填报项目
   ↓
7. 用户可以：
   - 点击"立即填报"按钮 → 在新标签页打开项目详情页
   - 点击"前往填报"按钮 → 跳转到月度报告仪表板
   - 点击"稍后处理" → 关闭弹窗，10 分钟后再次提醒
```

### 场景 2：完成填报后

```
1. 用户在月度报告表单中填写内容
   ↓
2. 点击"提交"按钮
   ↓
3. 系统保存报告，状态变为'submitted'
   ↓
4. 下次检查时，API 返回空列表
   ↓
5. 不再显示提醒弹窗
```

### 场景 3：非最后 5 天

```
1. 用户登录系统
   ↓
2. 中间件检测到不是每月最后 5 天
   ↓
3. 清除 session 中的提醒信息
   ↓
4. JavaScript 调用 API，返回"当前不是每月最后 5 天"
   ↓
5. 不显示弹窗
```

## 测试方法

### 手动测试脚本

**文件**: `test_monthly_report_reminder.py`

```bash
# 运行测试
python test_monthly_report_reminder.py
```

测试内容：
1. ✅ 检查今天是否为每月最后 5 天
2. ✅ 遍历所有活跃用户
3. ✅ 检查每个用户是否有待填报的项目
4. ✅ 输出详细的测试结果

### 浏览器测试步骤

1. **确认时间**：确保当前日期是每月最后 5 天（26-30/31 日）
2. **分配项目**：确保测试用户在 `ProjectReporter` 中有待填报的项目
3. **登录系统**：用测试账号登录
4. **观察弹窗**：2 秒后应该看到提醒弹窗
5. **检查定时器**：关闭弹窗后，等待 10 分钟，应该会再次弹出
6. **完成填报**：填报一个项目后刷新页面，该项目的提醒应该消失

## 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 提醒周期 | 每月最后 5 天 | 26 日到月末 |
| 重复提醒间隔 | 10 分钟 (600000ms) | 两次提醒之间的最小时间间隔 |
| 首次延迟 | 2 秒 (2000ms) | 页面加载后延迟显示，避免干扰 |
| 模态框类型 | 静态背景 (`backdrop: 'static'`) | 必须手动关闭，不能点击背景关闭 |

## 数据库模型依赖

### ProjectReporter（项目填报人员关联表）
```python
class ProjectReporter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE)
    report_period = models.CharField(max_length=20, choices=REPORT_PERIOD_CHOICES, default='monthly')
    is_active = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
```

### MonthlyReport（月度报告）
```python
class MonthlyReport(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE)
    report_year = models.IntegerField()
    report_month = models.CharField(max_length=7)  # YYYY-MM
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='draft')
    # ... 其他字段
```

## 注意事项

### 1. 时间计算
- 使用服务器系统时间，确保服务器时区正确
- 跨月时的边界情况已处理（12 月→次年 1 月）

### 2. 性能优化
- 使用 `select_related()` 预加载关联对象
- 只查询 `is_active=True` 和`monthly_report_required=True` 的项目
- 排除草稿状态（`status='draft'`）的报告

### 3. 用户体验
- 延迟 2 秒显示，避免干扰页面加载
- 模态框可关闭，但会定时再次提醒
- 提供多个操作入口（立即填报、前往填报）
- 显示项目编号和名称，方便识别

### 4. 浏览器兼容性
- 使用 jQuery（已在 base.html 中引入）
- Bootstrap 5 Modal 组件
- Fetch API（现代浏览器均支持）

## 相关文件清单

### 后端文件
- ✅ `eims_app/middleware/monthly_report_reminder.py` - 提醒中间件
- ✅ `eims_app/views/views_monthly_report.py` - API 视图（新增 2 个函数）
- ✅ `eims_app/models/model_user.py` - ProjectReporter、MonthlyReport 模型（已存在）

### 前端文件
- ✅ `eims_app/templates/base/base.html` - 基础模板（添加 JavaScript 代码）

### 配置文件
- ✅ `settings.py` - 注册中间件
- ✅ `eims_app/urls.py` - 添加 API 路由

### 测试文件
- ✅ `test_monthly_report_reminder.py` - 测试脚本

## 完成时间

2026 年 3 月 29 日

---

**开发者备注**：此功能通过中间件、API 和前端 JavaScript 的协同工作，实现了智能、友好的月度报告提醒机制。既保证了提醒的及时性，又避免了过度打扰用户。
