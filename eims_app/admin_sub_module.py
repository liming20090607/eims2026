"""
子模块权限管理 - 在 Django Admin 中配置不同公司的子模块权限
"""
from django.contrib import admin
from .models.model_tenant import Tenant
from .models.model_tenant_module import TenantModule
from .models.model_sub_module import SubModule, TenantSubModulePermission


@admin.register(SubModule)
class SubModuleAdmin(admin.ModelAdmin):
    """子模块定义管理"""
    
    list_display = ('parent_module', 'code', 'name', 'icon', 'sort_order', 'is_active', 'create_time')
    list_filter = ('parent_module', 'is_active')
    search_fields = ('code', 'name', 'parent_module__name')
    ordering = ('parent_module__sort_order', 'sort_order', 'code')
    list_editable = ('sort_order', 'is_active')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('parent_module', 'code', 'name', 'icon'),
            'description': '设置子模块的基本信息'
        }),
        ('URL配置', {
            'fields': ('url_name', 'url_pattern'),
            'description': '设置子模块的URL，url_name用于链接，url_pattern用于高亮当前菜单'
        }),
        ('显示配置', {
            'fields': ('description', 'sort_order', 'is_active'),
            'description': '设置子模块的排序和启用状态'
        }),
    )
    
    actions = ['enable_selected', 'disable_selected']
    
    def enable_selected(self, request, queryset):
        """批量启用选中的子模块"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'已启用 {updated} 个子模块')
    
    enable_selected.short_description = '✓ 启用选中的子模块'
    
    def disable_selected(self, request, queryset):
        """批量禁用选中的子模块"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'已禁用 {updated} 个子模块')
    
    disable_selected.short_description = '✗ 禁用选中的子模块'


class TenantSubModulePermissionInline(admin.TabularInline):
    """租户子模块权限内联 - 在租户详情页编辑子模块权限"""
    
    model = TenantSubModulePermission
    extra = 0
    fields = ('sub_module', 'is_enabled')
    can_delete = False
    show_change_link = True
    
    def get_formset(self, request, obj=None, **kwargs):
        """只显示属于已启用一级模块的子模块"""
        formset = super().get_formset(request, obj, **kwargs)
        if obj:  # 编辑租户时
            # 获取该租户已启用的一级模块ID列表
            from .models.model_tenant_module import TenantModulePermission
            enabled_module_ids = list(TenantModulePermission.objects.filter(
                tenant=obj,
                is_enabled=True
            ).values_list('module', flat=True))
            
            # 过滤子模块，只显示属于已启用一级模块的子模块
            if enabled_module_ids:
                formset.form.base_fields['sub_module'].queryset = SubModule.objects.filter(
                    parent_module_id__in=enabled_module_ids,
                    is_active=True
                ).order_by('parent_module__sort_order', 'sort_order')
            else:
                formset.form.base_fields['sub_module'].queryset = SubModule.objects.none()
        return formset
    
    def has_add_permission(self, request, obj=None):
        """不允许手动添加，由系统自动创建"""
        return False


# 更新 TenantAdmin 的 inlines，添加子模块权限
# 需要修改 admin_tenant_module.py 中的 TenantAdmin
@admin.register(TenantSubModulePermission)
class TenantSubModulePermissionAdmin(admin.ModelAdmin):
    """
    租户子模块权限管理
    
    使用方式:
    1. 方式一：在"租户公司"详情页，直接编辑"子模块权限"内联表单
    2. 方式二：在本页面按公司筛选，批量设置子模块权限
    
    提示：勾选表示该公司可以使用此子模块，不勾选则隐藏该子模块
    """
    
    list_display = ('tenant', 'sub_module', 'get_parent_module', 'is_enabled', 'update_time')
    list_filter = ('tenant', 'sub_module__parent_module', 'is_enabled')
    search_fields = ('tenant__name', 'sub_module__name', 'sub_module__parent_module__name')
    ordering = ('tenant', 'sub_module__parent_module__sort_order', 'sub_module__sort_order')
    list_editable = ('is_enabled',)
    
    fieldsets = (
        ('权限配置', {
            'fields': ('tenant', 'sub_module', 'is_enabled'),
            'description': '勾选"是否启用"表示该公司可以使用此子模块'
        }),
    )
    
    actions = ['enable_selected', 'disable_selected']
    
    def get_parent_module(self, obj):
        """获取父模块名称"""
        return obj.sub_module.parent_module.name
    
    get_parent_module.short_description = '所属一级模块'
    
    def enable_selected(self, request, queryset):
        """批量启用选中的子模块权限"""
        updated = queryset.update(is_enabled=True)
        self.message_user(request, f'已启用 {updated} 条子模块权限')
    
    enable_selected.short_description = '✓ 启用选中的子模块'
    
    def disable_selected(self, request, queryset):
        """批量禁用选中的子模块权限"""
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f'已禁用 {updated} 条子模块权限')
    
    disable_selected.short_description = '✗ 禁用选中的子模块'
