from django.contrib import admin
from django.contrib.auth.models import User
from eims_app.models.model_contract import Contract  # 导入合同模型，路径确保正确
from .models.model_project import Project
from .models.model_output_payment import OutputPayment
from .models.model_personnel import Personnel
from .models.model_employee import Employee
from .models.model_project_dynamic import ProjectDynamic
from .models.model_user import UserProfile
from .models.model_dynamic_choice import DynamicChoice

# 导入自定义的用户管理配置
from .admin_user import UserAdmin, UserProfileAdmin

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'project_name', 'project_category', 'project_status', 'contract_count')
    search_fields = ('project_code', 'project_name', 'project_director')
    list_filter = ('project_category', 'project_status')

@admin.register(OutputPayment)
class OutputPaymentAdmin(admin.ModelAdmin):
    list_display = ('project', 'month', 'monthly_output', 'cumulative_output', 'actual_payment')
    search_fields = ('project__project_code', 'project__project_name', 'month')
    list_filter = ('month', 'project')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'name', 'gender', 'mobile', 'education', 'ethnic', 'entry_time')
    search_fields = ('employee_code', 'name', 'mobile', 'id_card')
    list_filter = ('gender', 'education', 'ethnic')

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
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'contract_type', 'project_code', 'contract_code', 'contract_name',
        'party_a', 'contract_amount', 'signing_time', 'status'
    )
    list_filter = (
        'contract_type', 'status', 'signing_time'
    )
    search_fields = (
        'project_code', 'contract_code', 'contract_name', 'party_a'
    )

@admin.register(DynamicChoice)
class DynamicChoiceAdmin(admin.ModelAdmin):
    list_display = ('category', 'code', 'name', 'order', 'is_active', 'created_by', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('category', 'code', 'name')
    ordering = ('category', 'order')
    list_editable = ('order', 'is_active')
