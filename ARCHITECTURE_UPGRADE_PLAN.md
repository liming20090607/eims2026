# EIMS2026 多租户定制化架构升级方案

## 📊 现状分析

### ✅ 已有的能力

1. **数据隔离**：每个公司有独立的数据库
2. **审批链配置**：支持3级审批，可配置部门和角色
3. **高管角色配置**：可为不同公司配置不同的管理层级
4. **部门角色配置**：每个公司可以有自己的组织架构

### ❌ 当前的局限

1. **代码完全相同**：所有公司使用同一套views、forms、templates
2. **字段无法定制**：合同/项目台账的字段对所有公司都一样
3. **流程逻辑固定**：虽然可以配置审批人，但业务逻辑硬编码
4. **表单验证统一**：无法为不同公司设置不同的验证规则

---

## 🎯 推荐方案：配置驱动 + 插件化扩展

采用**渐进式架构**，分三个阶段实施：

### 第一阶段：增强配置能力（立即实施）⭐

#### 目标
通过配置解决80%的差异化需求，无需修改代码。

#### 实施内容

##### 1. 创建租户配置模型

```python
# eims_app/models/model_tenant_config.py

class TenantModuleConfig(BaseModel):
    """租户模块配置 - 控制各模块的显示和字段"""
    
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='module_configs')
    module_name = models.CharField(max_length=50, verbose_name='模块名称', 
                                   help_text='如：contract_management, project_detail')
    
    # 字段配置
    visible_fields = JSONField(default=list, verbose_name='可见字段',
                              help_text='JSON数组，如：["contract_no", "party_a", "amount"]')
    required_fields = JSONField(default=list, verbose_name='必填字段',
                               help_text='JSON数组，如：["contract_no", "amount"]')
    field_labels = JSONField(default=dict, verbose_name='字段标签',
                            help_text='自定义字段显示名称')
    
    # 列表页配置
    list_display = JSONField(default=list, verbose_name='列表显示字段')
    list_filter = JSONField(default=list, verbose_name='列表筛选字段')
    search_fields = JSONField(default=list, verbose_name='搜索字段')
    
    # 权限配置
    can_add = models.BooleanField(default=True, verbose_name='是否可新增')
    can_edit = models.BooleanField(default=True, verbose_name='是否可编辑')
    can_delete = models.BooleanField(default=False, verbose_name='是否可删除')
    can_export = models.BooleanField(default=True, verbose_name='是否可导出')
    
    class Meta:
        unique_together = ['tenant', 'module_name']
        verbose_name = '模块配置'
        verbose_name_plural = '模块配置管理'


class ContractFieldConfig(BaseModel):
    """合同字段个性化配置"""
    
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='contract_field_configs')
    field_name = models.CharField(max_length=50, verbose_name='字段名')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    is_required = models.BooleanField(default=False, verbose_name='是否必填')
    display_order = models.IntegerField(default=0, verbose_name='显示顺序')
    validation_rules = JSONField(null=True, blank=True, verbose_name='验证规则',
                                help_text='如：{"min_value": 0, "max_length": 200}')
    custom_label = models.CharField(max_length=100, blank=True, verbose_name='自定义标签')
    help_text = models.TextField(blank=True, verbose_name='帮助文本')
    
    class Meta:
        unique_together = ['tenant', 'field_name']
        verbose_name = '合同字段配置'
        verbose_name_plural = '合同字段配置管理'


class ApprovalWorkflowConfig(BaseModel):
    """审批工作流配置 - 支持条件分支"""
    
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='workflow_configs')
    business_type = models.CharField(max_length=50, verbose_name='业务类型',
                                    choices=[
                                        ('contract', '合同审批'),
                                        ('seal', '用印审批'),
                                        ('archive', '归档审批'),
                                        ('payment', '付款审批'),
                                    ])
    
    # 条件配置
    condition_field = models.CharField(max_length=50, blank=True, verbose_name='条件字段',
                                      help_text='如：amount, contract_type')
    condition_operator = models.CharField(max_length=20, blank=True, verbose_name='条件运算符',
                                         choices=[
                                             ('gt', '大于'),
                                             ('lt', '小于'),
                                             ('gte', '大于等于'),
                                             ('lte', '小于等于'),
                                             ('eq', '等于'),
                                             ('in', '在列表中'),
                                         ])
    condition_value = models.CharField(max_length=200, blank=True, verbose_name='条件值',
                                      help_text='如：1000000 或 ["type_a", "type_b"]')
    
    # 关联审批链
    approval_chain = models.ForeignKey('ApprovalChain', on_delete=models.PROTECT, 
                                      verbose_name='审批链',
                                      help_text='满足条件时使用的审批链')
    
    priority = models.IntegerField(default=100, verbose_name='优先级',
                                  help_text='数字越小优先级越高')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        verbose_name = '审批工作流配置'
        verbose_name_plural = '审批工作流配置管理'
        ordering = ['business_type', 'priority']
```

##### 2. 创建配置管理视图

```python
# eims_app/views/views_tenant_config.py

@login_required
def tenant_module_config(request):
    """租户模块配置管理"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        messages.error(request, '未找到租户信息')
        return redirect('eims_app:eims_index')
    
    configs = TenantModuleConfig.objects.filter(tenant=tenant)
    
    context = {
        'configs': configs,
        'title': '模块配置管理',
    }
    return render(request, 'config/module_config_list.html', context)


@login_required
def edit_module_config(request, module_name):
    """编辑模块配置"""
    tenant = getattr(request, 'tenant', None)
    
    config, created = TenantModuleConfig.objects.get_or_create(
        tenant=tenant,
        module_name=module_name,
        defaults={
            'visible_fields': [],
            'required_fields': [],
            'list_display': [],
        }
    )
    
    if request.method == 'POST':
        form = ModuleConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '配置保存成功')
            return redirect('eims_app:tenant_module_config')
    else:
        form = ModuleConfigForm(instance=config)
    
    context = {
        'form': form,
        'module_name': module_name,
        'title': f'配置模块：{module_name}',
    }
    return render(request, 'config/module_config_form.html', context)
```

##### 3. 修改现有视图以支持配置

```python
# eims_app/views/views_contract.py 示例

from eims_app.models.model_tenant_config import TenantModuleConfig, ContractFieldConfig

def contract_list(request):
    """合同列表 - 支持租户配置"""
    tenant = getattr(request, 'tenant', None)
    
    # 获取模块配置
    module_config = TenantModuleConfig.objects.filter(
        tenant=tenant,
        module_name='contract_management'
    ).first()
    
    # 获取字段配置
    field_configs = ContractFieldConfig.objects.filter(
        tenant=tenant
    ).order_by('display_order')
    
    # 构建可见字段列表
    visible_fields = module_config.list_display if module_config else [
        'contract_no', 'project_name', 'party_a', 'amount', 'sign_date'
    ]
    
    # 查询数据
    contracts = Contract.objects.filter(tenant=tenant).order_by('-created_at')
    
    context = {
        'contracts': contracts,
        'visible_fields': visible_fields,
        'field_configs': {fc.field_name: fc for fc in field_configs},
        'can_add': module_config.can_add if module_config else True,
        'can_export': module_config.can_export if module_config else True,
        'title': '合同管理',
    }
    return render(request, 'contract_management/contract_list.html', context)
```

##### 4. 修改模板以支持动态字段

```html
<!-- eims_app/templates/contract_management/contract_list.html -->

<table class="table table-striped">
    <thead>
        <tr>
            {% for field in visible_fields %}
            <th>
                {% if field in field_configs and field_configs[field].custom_label %}
                    {{ field_configs[field].custom_label }}
                {% else %}
                    {{ field|verbose_name }}
                {% endif %}
            </th>
            {% endfor %}
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        {% for contract in contracts %}
        <tr>
            {% for field in visible_fields %}
            <td>{{ contract|get_attr:field }}</td>
            {% endfor %}
            <td>
                <a href="{% url 'eims_app:contract_detail' contract.pk %}" class="btn btn-sm btn-info">查看</a>
                {% if can_edit %}
                <a href="{% url 'eims_app:contract_edit' contract.pk %}" class="btn btn-sm btn-warning">编辑</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

需要添加模板过滤器：

```python
# eims_app/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    """获取对象的属性值"""
    return getattr(obj, attr_name, '')

@register.filter
def verbose_name(field_name):
    """获取字段的verbose_name"""
    from eims_app.models import Contract
    try:
        field = Contract._meta.get_field(field_name)
        return field.verbose_name or field_name
    except:
        return field_name
```

#### 优点
- ✅ 无需修改核心代码结构
- ✅ 管理员可通过后台界面配置
- ✅ 快速响应客户需求变化
- ✅ 维护成本低

#### 缺点
- ❌ 复杂的业务逻辑仍需要代码实现
- ❌ UI定制能力有限

---

### 第二阶段：插件化扩展（当配置不够用时）

#### 目标
允许为特定公司编写定制化的业务逻辑。

#### 实施思路

##### 1. 创建插件基类

```python
# eims_app/plugins/base.py

class BasePlugin:
    """插件基类"""
    
    name = ''
    description = ''
    tenant_id = None  # 指定适用的租户，None表示通用
    
    def validate_contract(self, data):
        """验证合同数据 - 可被子类重写"""
        return True, []
    
    def modify_contract_queryset(self, queryset, request):
        """修改合同查询集 - 可被子类重写"""
        return queryset
    
    def get_custom_fields(self):
        """获取自定义字段 - 可被子类重写"""
        return []
    
    def before_contract_save(self, contract, request):
        """合同保存前钩子"""
        pass
    
    def after_contract_save(self, contract, request):
        """合同保存后钩子"""
        pass
```

##### 2. 创建公司特定插件

```python
# eims_app/plugins/dingce_plugin.py

from .base import BasePlugin

class DingcePlugin(BasePlugin):
    name = 'dingce'
    description = '广西鼎策定制插件'
    tenant_id = 2  # 鼎策的tenant_id
    
    def validate_contract(self, data):
        errors = []
        
        # 鼎策特有验证：合同金额超过100万需要特殊说明
        if data.get('amount', 0) > 1000000 and not data.get('special_note'):
            errors.append('合同金额超过100万，请填写特殊说明')
        
        # 鼎策特有验证：必须有监理单位
        if not data.get('supervisor_unit'):
            errors.append('鼎策规定：合同必须填写监理单位')
        
        return len(errors) == 0, errors
    
    def modify_contract_queryset(self, queryset, request):
        # 鼎策特有的过滤逻辑
        user = request.user
        if not user.is_superuser:
            # 只显示用户参与的项目的合同
            queryset = queryset.filter(
                project__personnel__employee__user=user
            )
        return queryset
    
    def get_custom_fields(self):
        return [
            {
                'name': 'supervisor_unit',
                'label': '监理单位',
                'type': 'text',
                'required': True,
            },
            {
                'name': 'quality_grade',
                'label': '质量等级',
                'type': 'select',
                'choices': [('excellent', '优良'), ('good', '合格'), ('pass', '通过')],
            }
        ]
```

##### 3. 插件管理器

```python
# eims_app/plugins/manager.py

import os
import importlib
from django.conf import settings

class PluginManager:
    _plugins = {}
    
    @classmethod
    def load_plugins(cls):
        """加载所有插件"""
        plugin_dir = os.path.join(settings.BASE_DIR, 'eims_app', 'plugins')
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith('_plugin.py'):
                module_name = filename[:-3]
                module = importlib.import_module(f'eims_app.plugins.{module_name}')
                
                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin):
                        plugin = attr()
                        cls._plugins[plugin.name] = plugin
    
    @classmethod
    def get_plugin_for_tenant(cls, tenant_id):
        """获取适用于指定租户的插件"""
        for plugin in cls._plugins.values():
            if plugin.tenant_id == tenant_id:
                return plugin
        return None
    
    @classmethod
    def execute_hook(cls, hook_name, tenant_id, *args, **kwargs):
        """执行插件钩子"""
        plugin = cls.get_plugin_for_tenant(tenant_id)
        if plugin and hasattr(plugin, hook_name):
            method = getattr(plugin, hook_name)
            return method(*args, **kwargs)
        return None

# 在Django启动时加载插件
# eims_app/apps.py
class EimsAppConfig(AppConfig):
    def ready(self):
        from .plugins.manager import PluginManager
        PluginManager.load_plugins()
```

##### 4. 在视图中调用插件

```python
# eims_app/views/views_contract.py

from eims_app.plugins.manager import PluginManager

def contract_create(request):
    """创建合同 - 支持插件扩展"""
    tenant = getattr(request, 'tenant', None)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 执行插件验证
            is_valid, errors = PluginManager.execute_hook(
                'validate_contract',
                tenant.id if tenant else None,
                form.cleaned_data
            )
            
            if is_valid is False:
                for error in errors:
                    form.add_error(None, error)
            else:
                contract = form.save(commit=False)
                contract.tenant = tenant
                
                # 执行保存前钩子
                PluginManager.execute_hook(
                    'before_contract_save',
                    tenant.id if tenant else None,
                    contract,
                    request
                )
                
                contract.save()
                
                # 执行保存后钩子
                PluginManager.execute_hook(
                    'after_contract_save',
                    tenant.id if tenant else None,
                    contract,
                    request
                )
                
                messages.success(request, '合同创建成功')
                return redirect('eims_app:contract_list')
    else:
        form = ContractForm()
    
    # 获取自定义字段
    custom_fields = PluginManager.execute_hook(
        'get_custom_fields',
        tenant.id if tenant else None
    ) or []
    
    context = {
        'form': form,
        'custom_fields': custom_fields,
        'title': '创建合同',
    }
    return render(request, 'contract_management/contract_form.html', context)
```

#### 优点
- ✅ 可以实现完全不同的业务逻辑
- ✅ 保持代码隔离，互不影响
- ✅ 易于测试和维护
- ✅ 支持热插拔

#### 缺点
- ❌ 需要一定的开发能力
- ❌ 插件数量增多后管理复杂

---

### 第三阶段：按需拆分（未来可能需要）

如果某家公司需求特别复杂，可以考虑将其拆分为独立的Django项目，共享公共模块。

---

## 🚀 立即行动计划

### Week 1: 基础配置框架

1. ✅ 创建 `TenantModuleConfig` 和 `ContractFieldConfig` 模型
2. ✅ 创建配置管理视图和表单
3. ✅ 添加必要的模板过滤器
4. ✅ 修改合同列表视图以支持配置

### Week 2: 审批流程增强

1. ✅ 创建 `ApprovalWorkflowConfig` 模型支持条件分支
2. ✅ 修改审批链视图以支持动态层级
3. ✅ 实现基于条件的审批链选择逻辑

### Week 3: 项目台账定制

1. ✅ 创建 `ProjectFieldConfig` 模型
2. ✅ 修改项目相关视图以支持配置
3. ✅ 更新项目表单和列表模板

### Week 4: 测试和优化

1. ✅ 为每家公司配置不同的字段和流程
2. ✅ 测试各种场景
3. ✅ 优化性能和用户体验

---

## 💡 总结

您当前的系统架构**完全适用**于多租户定制化需求，只需要：

1. **短期**：增强配置能力（1个月即可完成）
2. **中期**：引入插件机制（按需实施）
3. **长期**：必要时拆分独立项目（很少需要）

**关键优势**：
- ✅ 已有良好的数据隔离基础
- ✅ 已有审批链配置框架
- ✅ Django的灵活性支持渐进式演进
- ✅ 不需要推倒重来

**建议从第一阶段开始**，先实现配置驱动的定制，这已经能解决大部分需求。当遇到配置无法满足的场景时，再考虑引入插件机制。

需要我帮您开始实施第一阶段的代码吗？
