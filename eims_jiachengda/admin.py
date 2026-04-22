from django.contrib import admin
from django.contrib.auth.models import User, Group
from eims_app.models.model_contract import Contract  # 导入合同模型，路径确保正确
# from .models.model_project import Project  # 已废弃，使用 ProjectDetail 替代
from .models.model_output_payment import OutputPayment
from .models.model_personnel import Personnel
from .models.model_employee import Employee
from .models.model_project_detail import ProjectDetail
from .models.model_project_dynamic import ProjectDynamic
from .models.model_user import UserProfile
from .models.model_dynamic_choice import DynamicChoice
from .models.model_tenant import Tenant
from .models.model_tenant_module import TenantModule, TenantModulePermission

# 导入自定义的用户管理配置
from .admin_user import UserAdmin, UserProfileAdmin

# 导入租户模块权限管理配置（包含 TenantAdmin, TenantModuleAdmin, TenantModulePermissionAdmin）
from . import admin_tenant_module

# 导入导入导出功能
try:
    from import_export.admin import ImportExportModelAdmin
    from import_export import resources
    IMPORT_EXPORT_AVAILABLE = True
    
    # 创建 Resource 类
    # class ProjectResource(resources.ModelResource):  # 已废弃
    #     class Meta:
    #         model = Project
    #         import_id_fields = ('id',)
    
    class ProjectDetailResource(resources.ModelResource):
        class Meta:
            model = ProjectDetail
            import_id_fields = ('id',)
    
    class EmployeeResource(resources.ModelResource):
        class Meta:
            model = Employee
            import_id_fields = ('id',)
    
    class ContractResource(resources.ModelResource):
        class Meta:
            model = Contract
            import_id_fields = ('id',)
    
except ImportError:
    IMPORT_EXPORT_AVAILABLE = False
    print("提示：安装 django-import-export 以启用导入导出功能")
    print("命令：pip install django-import-export")

# Project 已废弃，使用 ProjectDetail 替代
@admin.register(ProjectDetail)
class ProjectDetailAdmin(ImportExportModelAdmin if IMPORT_EXPORT_AVAILABLE else admin.ModelAdmin):
    list_display = ('project_code', 'project_name', 'contract_category', 'project_status', 'contract_status')
    search_fields = ('project_code', 'project_name', 'project_director', 'contract_code')
    list_filter = ('contract_category', 'project_status', 'contract_status')
    if IMPORT_EXPORT_AVAILABLE:
        resource_classes = [ProjectDetailResource]

@admin.register(OutputPayment)
class OutputPaymentAdmin(admin.ModelAdmin):
    list_display = ('project', 'month', 'monthly_output', 'cumulative_output', 'actual_payment')
    search_fields = ('project__project_code', 'project__project_name', 'month')
    list_filter = ('month', 'project')

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin if IMPORT_EXPORT_AVAILABLE else admin.ModelAdmin):
    list_display = ('personnel_code', 'name', 'gender', 'mobile', 'education', 'ethnic', 'entry_time')
    search_fields = ('employee_code', 'name', 'mobile', 'id_card')
    list_filter = ('gender', 'education', 'ethnic')
    if IMPORT_EXPORT_AVAILABLE:
        resource_classes = [EmployeeResource]

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('personnel_code', 'name', 'project', 'position', 'entry_time')
    search_fields = ('personnel_code', 'name', 'project__project_name')
    list_filter = ('project', 'position', 'gender')

@admin.register(ProjectDynamic)
class ProjectDynamicAdmin(admin.ModelAdmin):
    list_display = ('project', 'project_progress', 'project_status', 'update_time')
    search_fields = ('project__project_code', 'project__project_name')
    list_filter = ('project_status', 'project')

@admin.register(Contract)
class ContractAdmin(ImportExportModelAdmin if IMPORT_EXPORT_AVAILABLE else admin.ModelAdmin):
    list_display = (
        'id', 'contract_type', 'project_code', 'contract_code', 'contract_name',
        'party_a', 'contract_amount', 'signing_time', 'status'
    )
    search_fields = ('contract_name', 'party_a', 'contract_code')
    list_filter = ('contract_type', 'status')
    if IMPORT_EXPORT_AVAILABLE:
        resource_classes = [ContractResource]

@admin.register(DynamicChoice)
class DynamicChoiceAdmin(admin.ModelAdmin):
    list_display = ('category', 'code', 'name', 'order', 'is_active', 'created_by', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('category', 'code', 'name')
    ordering = ('category', 'order')
    list_editable = ('order', 'is_active')

# 自定义 Group Admin，优化权限选择框显示
class CustomGroupAdmin(admin.ModelAdmin):
    """
    自定义 Group Admin 配置
    功能：优化权限选择框（filter_horizontal）的显示，加大加高选择框，增大文字
    """
    filter_horizontal = ('permissions',)
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

# 注销默认的 Group Admin 并注册自定义的
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
