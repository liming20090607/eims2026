"""
为各公司创建独立的高管角色Admin后台入口
使用租户特定的URL来访问Admin，确保数据隔离
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from django.views.generic import RedirectView

# 为每个租户创建自定义Admin site
class TenantAdminSite(admin.AdminSite):
    """租户专属Admin站点"""
    site_header = '公司管理后台'
    site_title = '公司管理后台'
    index_title = '管理控制台'

# 创建各公司的Admin站点
dingce_admin = TenantAdminSite(name='dingce_admin')
shengchang_admin = TenantAdminSite(name='shengchang_admin') 
jiachengda_admin = TenantAdminSite(name='jiachengda_admin')

# 注册CompanyExecutiveRole到各Admin站点
from eims_app.models import CompanyExecutiveRole

@admin.register(CompanyExecutiveRole)
class CompanyExecutiveRoleAdmin(admin.ModelAdmin):
    """公司高管角色管理"""
    list_display = ['user', 'executive_type', 'role_name', 'is_primary', 'order', 'tenant']
    list_filter = ['executive_type', 'is_primary', 'tenant']
    search_fields = ['user__username', 'user__first_name', 'role_name']
    ordering = ['tenant', 'order', 'executive_type']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('tenant', 'user', 'executive_type', 'role_name')
        }),
        ('职责配置', {
            'fields': ('is_primary', 'description', 'approval_authority'),
            'classes': ('collapse',)
        }),
        ('排序', {
            'fields': ('order',),
        }),
    )
    
    def get_queryset(self, request):
        """按租户过滤数据"""
        qs = super().get_queryset(request)
        
        # 超级管理员可以看到所有数据
        if request.user.is_superuser:
            return qs
        
        # 普通用户只能看到自己租户的数据
        if hasattr(request, 'current_tenant') and request.current_tenant:
            return qs.filter(tenant=request.current_tenant)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """过滤外键字段"""
        if db_field.name == 'tenant':
            # 超级管理员可以选择所有租户
            if request.user.is_superuser:
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            
            # 普通用户只能看到自己的租户
            if hasattr(request, 'current_tenant') and request.current_tenant:
                kwargs["queryset"] = type(db_field.remote_field.model).objects.filter(
                    id=request.current_tenant.id
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# 在每个Admin站点注册模型
for admin_site in [dingce_admin, shengchang_admin, jiachengda_admin]:
    admin_site.register(CompanyExecutiveRole, CompanyExecutiveRoleAdmin)

print("✓ 租户专用Admin配置已创建")
print("\n访问地址:")
print("  鼎策: http://127.0.0.1:8000/dingce/admin/")
print("  晟昌: http://127.0.0.1:8000/shengchang/admin/")
print("  嘉诚达: http://127.0.0.1:8000/jiachengda/admin/")
print("\n超级管理员仍可使用: http://127.0.0.1:8000/admin/")
