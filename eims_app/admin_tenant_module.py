"""
租户模块权限管理 - 在 Django Admin 中配置不同公司可用的业务模块
"""
from django.contrib import admin
from .models.model_tenant import Tenant
from .models.model_tenant_module import TenantModule, TenantModulePermission


@admin.register(TenantModule)
class TenantModuleAdmin(admin.ModelAdmin):
    """业务模块管理 - 定义系统可用的所有业务模块"""
    
    list_display = ('code', 'name', 'icon', 'sort_order', 'is_active', 'create_time')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    ordering = ('sort_order', 'code')
    list_editable = ('sort_order', 'is_active')
    
    fieldsets = (
        ('模块信息', {
            'fields': ('code', 'name', 'icon', 'description'),
            'description': '设置业务模块的基本信息'
        }),
        ('显示配置', {
            'fields': ('sort_order', 'is_active'),
            'description': '设置模块的排序和启用状态'
        }),
    )


class TenantModulePermissionInline(admin.TabularInline):
    """租户模块权限内联 - 在租户详情页直接编辑模块权限"""
    
    model = TenantModulePermission
    extra = 0
    fields = ('module', 'is_enabled')
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        """不允许手动添加，由系统自动创建"""
        return False


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """租户（公司）管理"""
    
    list_display = ('code', 'name', 'short_name', 'is_active', 'get_user_count', 'get_project_count', 'create_time')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'short_name')
    ordering = ('code',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'short_name', 'logo'),
            'description': '设置公司的基本信息和标识'
        }),
        ('联系信息', {
            'fields': ('contact_person', 'contact_phone', 'contact_email', 'address'),
            'description': '设置公司的联系方式'
        }),
        ('状态', {
            'fields': ('is_active', 'remark'),
            'description': '设置公司启用状态和备注'
        }),
    )
    
    inlines = [TenantModulePermissionInline]
    
    def get_user_count(self, obj):
        """获取活跃用户数量"""
        return obj.get_active_user_count()
    
    get_user_count.short_description = '活跃用户'
    
    def get_project_count(self, obj):
        """获取项目数量"""
        return obj.get_project_count()
    
    get_project_count.short_description = '项目数'


@admin.register(TenantModulePermission)
class TenantModulePermissionAdmin(admin.ModelAdmin):
    """
    租户模块权限管理
    
    使用方式:
    1. 方式一：在"租户公司"详情页，直接编辑"业务模块权限"内联表单
    2. 方式二：在本页面按公司筛选，批量设置模块权限
    
    提示：勾选表示该公司可以使用此模块，不勾选则隐藏该模块
    """
    
    list_display = ('tenant', 'module', 'is_enabled', 'update_time')
    list_filter = ('tenant', 'module', 'is_enabled')
    search_fields = ('tenant__name', 'module__name')
    ordering = ('tenant', 'module__sort_order')
    list_editable = ('is_enabled',)
    
    fieldsets = (
        ('权限配置', {
            'fields': ('tenant', 'module', 'is_enabled'),
            'description': '勾选"是否启用"表示该公司可以使用此模块'
        }),
    )
    
    actions = ['enable_selected', 'disable_selected']
    
    def enable_selected(self, request, queryset):
        """批量启用选中的模块权限"""
        updated = queryset.update(is_enabled=True)
        self.message_user(request, f'已启用 {updated} 条模块权限')
    
    enable_selected.short_description = '✓ 启用选中的模块'
    
    def disable_selected(self, request, queryset):
        """批量禁用选中的模块权限"""
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f'已禁用 {updated} 条模块权限')
    
    disable_selected.short_description = '✗ 禁用选中的模块'
