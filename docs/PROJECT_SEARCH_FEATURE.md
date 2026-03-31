# 项目详情页面模糊搜索功能实现说明

## 功能概述

在项目详情页面添加了模糊搜索框，支持通过以下关键字段筛选并定位到第一个符合条件的项目：
- 项目编号
- 项目名称
- 项目地址
- 合同甲方
- 合同乙方
- 合同编号

## 实现内容

### 1. 前端模板修改

**文件**: `eims_app/templates/project_ledger/detail.html`

#### 1.1 添加 CSS 样式 (行 15-69)
```css
/* 搜索框样式 */
.project-search-box {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: auto;
}

.project-search-input {
    width: 350px;
    padding: 4px 8px;
    font-size: 12px;
    border: 1px solid #ced4da;
    border-radius: 3px;
    outline: none;
    transition: all 0.2s ease;
}

.project-search-input:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.project-search-btn {
    padding: 4px 12px;
    font-size: 12px;
    min-width: 60px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
}

.search-result-info {
    font-size: 11px;
    color: #28a745;
    font-weight: 500;
    margin-left: 8px;
    display: none;
}

.search-error-info {
    font-size: 11px;
    color: #dc3545;
    font-weight: 500;
    margin-left: 8px;
    display: none;
}
```

#### 1.2 添加搜索框 UI (行 553-567)
在导航按钮旁边添加搜索框组件：
```html
<!-- 搜索框 -->
<div class="project-search-box">
    <input type="text" 
           id="projectSearchInput" 
           class="project-search-input" 
           placeholder="搜索：项目编号/名称/地址/甲方/乙方..."
           autocomplete="off">
    <button class="btn btn-primary btn-sm project-search-btn" onclick="searchAndNavigate()">
        <i class="bi bi-search"></i> 搜索
    </button>
    <span id="searchResultInfo" class="search-result-info"></span>
    <span id="searchErrorInfo" class="search-error-info"></span>
</div>
```

#### 1.3 添加 JavaScript 搜索逻辑 (行 1231-1299)
实现 AJAX 搜索和导航功能：
- `searchAndNavigate()` 函数：发送 AJAX 请求并处理响应
- 回车键支持：监听 Enter 键触发搜索
- 结果提示：显示找到的项目信息
- 自动导航：延迟 500ms 后跳转到项目详情页

### 2. 后端 API 实现

**文件**: `eims_app/views/views_project_ledger.py`

#### 2.1 导入 JsonResponse (行 8)
```python
from django.http import JsonResponse
```

#### 2.2 创建 API 视图函数 (行 925-967)
```python
@login_required
def project_search_api(request):
    """项目搜索 API - 返回 JSON 格式的第一个匹配结果"""
    
    # 获取搜索关键词
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'success': False, 'error': '请输入搜索关键词'})
    
    try:
        # 基础查询集
        queryset = ProjectDetail.objects.all()
        
        # 多条件模糊搜索（返回第一个匹配的结果）
        project = queryset.filter(
            Q(project_name__icontains=query) |          # 项目名称
            Q(project_address__icontains=query) |        # 项目地址
            Q(contract_party_a__icontains=query) |       # 合同甲方
            Q(contract_party_b__icontains=query) |       # 合同乙方
            Q(project_code__icontains=query) |           # 项目编号
            Q(contract_code__icontains=query)            # 合同编号
        ).first()
        
        if project:
            # 找到匹配的项目，返回基本信息
            return JsonResponse({
                'success': True,
                'match': {
                    'id': project.id,
                    'project_code': project.project_code,
                    'project_name': project.project_name,
                    'project_address': project.project_address or '',
                    'contract_party_a': project.contract_party_a,
                    'contract_party_b': project.contract_party_b,
                }
            })
        else:
            # 未找到匹配的项目
            return JsonResponse({'success': True, 'match': None})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
```

### 3. URL 路由配置

**文件**: `eims_app/urls.py`

#### 3.1 添加 API 路由 (行 282-284)
```python
# 项目搜索 API 路由（用于 AJAX 搜索）
path('api/projects/search/', views_project_ledger.project_search_api, name='project_search_api'),
```

## 技术特点

### 1. 模糊搜索实现
- 使用 Django ORM 的 `Q` 对象进行多字段 OR 查询
- `icontains` 实现不区分大小写的包含匹配
- 只返回第一个匹配结果，提高查询效率

### 2. 用户体验优化
- **实时反馈**: 搜索结果显示绿色成功提示或红色错误提示
- **延迟跳转**: 500ms 延迟让用户看到搜索结果再跳转
- **回车支持**: 可以直接按 Enter 键触发搜索
- **占位符提示**: 输入框显示支持的搜索字段

### 3. 权限控制
- 使用 `@login_required` 装饰器确保只有登录用户可访问
- 搜索框仅对超级管理员显示（与导航按钮一致）

### 4. 错误处理
- 空搜索词验证
- 数据库查询异常捕获
- 友好的错误提示信息

## 使用方法

1. **打开项目详情页**: 访问任意项目的详情页面
2. **输入搜索关键词**: 在搜索框中输入项目编号、名称、地址、甲方或乙方的关键字
3. **执行搜索**: 
   - 点击"搜索"按钮，或
   - 按 Enter 键
4. **查看结果**: 
   - 找到匹配：显示项目名称和编号，自动跳转到该项目详情页
   - 未找到：显示"未找到匹配的项目"提示
5. **继续搜索**: 可以输入新的关键词继续搜索

## 示例场景

### 场景 1：通过项目编号搜索
输入：`YLXF` (燕林学府项目编号的一部分)  
结果：快速定位到燕林学府项目详情页

### 场景 2：通过项目名称搜索
输入：`学府`  
结果：定位到第一个包含"学府"的项目

### 场景 3：通过甲方搜索
输入：`万科`  
结果：定位到第一个甲方为"万科"的项目

### 场景 4：通过地址搜索
输入：`江北`  
结果：定位到第一个地址包含"江北"的项目

## 性能考虑

1. **LIMIT 1 优化**: 使用 `.first()` 只获取第一条记录，避免不必要的数据加载
2. **索引利用**: ProjectDetail 模型在 `project_code`, `project_name` 等字段有数据库索引
3. **AJAX 异步**: 不刷新页面，提升用户体验
4. **防抖考虑**: 当前未实现防抖，如需频繁搜索可添加 debounce 功能

## 扩展建议

### 可能的改进方向
1. **高亮显示**: 在搜索结果中高亮匹配的关键词
2. **下拉提示**: 输入时显示匹配的前 N 个项目供选择
3. **高级搜索**: 支持组合条件搜索（如：状态 + 甲方）
4. **搜索历史**: 记录最近搜索的关键词
5. **导出结果**: 将搜索结果导出为 Excel

## 注意事项

1. **浏览器缓存**: 如果样式未生效，请按 `Ctrl+Shift+R` 强制刷新浏览器缓存
2. **权限要求**: 只有超级管理员才能看到搜索框（与导航按钮权限一致）
3. **字符编码**: 支持中文搜索，使用 `icontains` 进行模糊匹配
4. **特殊字符**: 搜索特殊字符时可能需要进行转义处理

## 相关文件清单

- ✅ `eims_app/templates/project_ledger/detail.html` - 前端模板
- ✅ `eims_app/views/views_project_ledger.py` - 后端视图
- ✅ `eims_app/urls.py` - URL 路由配置

## 测试验证

### 测试步骤
1. 启动开发服务器：`python manage.py runserver`
2. 以超级管理员身份登录
3. 访问任意项目详情页
4. 在搜索框输入测试关键词
5. 验证搜索结果和导航功能

### 预期结果
- ✅ 搜索框显示正常，样式美观
- ✅ 输入关键词后能正确搜索
- ✅ 找到项目时显示绿色提示信息
- ✅ 未找到项目时显示红色错误提示
- ✅ 自动跳转到第一个匹配项目的详情页
- ✅ 支持 Enter 键触发搜索
- ✅ 错误处理友好且准确

## 完成时间

2026 年 3 月 21 日

---

**开发者备注**: 此功能实现简洁高效，充分利用了 Django ORM 的查询能力和 AJAX 的异步特性，为用户提供了便捷的项目导航体验。
