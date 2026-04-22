from django.urls import path
from .views.views_project import (
    ProjectListView, ProjectCreateView, 
    ProjectUpdateView, ProjectDeleteView,
    ProjectDetailView, project_batch_delete,
    project_export, project_by_contract, project_import,
    import_project_dynamic, import_personnel,
    delete_dynamic, delete_personnel,
    add_dynamic, add_personnel
)
from .views.views_output_payment import (
    OutputPaymentListView, OutputPaymentCreateView, OutputPaymentUpdateView, OutputPaymentDetailView,
    import_output_payment, delete_output, add_output
)
from .views import views_contract
from .views.views_index import IndexView, system_navigation, module_welcome
from .views import views_cost_sub_modules
from .views.views_contract import (
    contract_list, contract_add, contract_edit, 
    contract_delete, contract_detail, contract_batch_delete,
    contract_import, contract_export, contract_import_template,
    contract_approval_chain, contract_approval_add, contract_approval_detail,
    contract_approval_edit, contract_approval_submit, contract_approval_approve,
    contract_approval_reject, contract_approval_cancel
)
from .views.views_archive_approval import (
    archive_approval_chain, archive_approval_add, archive_approval_detail,
    archive_approval_edit, archive_approval_submit, archive_approval_approve,
    archive_approval_reject, archive_approval_cancel
)
from .views.views_seal_approval import (
    seal_approval_list, seal_approval_add, seal_approval_detail,
    seal_approval_edit, seal_approval_submit, seal_approval_approve,
    seal_approval_reject, seal_approval_cancel, seal_approval_delete_attachment,
    get_department_personnel_ajax, seal_attachment_preview, seal_attachment_download
)
from .views.views_my_approvals import my_pending_approvals, my_initiated_approvals
from .views.views_profile import profile_view
from .views.views_my_account import my_account_view
from .views import views_personnel
from .views.views_employee import (
    employee_list, employee_add, employee_detail, 
    employee_edit, employee_delete, employee_batch_delete,
    employee_export
)
from .views.views_personnel_detail import (
    certificate_list, certificate_create, certificate_edit, certificate_delete, certificate_detail,
    allocation_list, allocation_create, allocation_edit, allocation_delete, allocation_detail
)
from .views.views_allocation_visual import (
    allocation_visual, allocate_personnel_ajax, assign_to_department_ajax, recall_personnel_ajax,
    update_personnel_allocation, delete_all_personnel_allocation,
    allocate_to_project_ajax, recall_to_company_ajax, recall_to_department_ajax,
    get_personnel_projects
)
from .views.views_department import (
    department_list, department_create, department_edit, department_delete, department_detail,
    department_role_list, department_role_create, department_role_edit, department_role_delete,
    approval_chain_list, approval_chain_create, approval_chain_edit, approval_chain_delete,
    organization_navigation, temp_welcome, add_role_type
)
from .views.views_personnel import (
    personnel_list, personnel_add, personnel_edit, personnel_delete, personnel_detail,
    personnel_navigation, personnel_import, personnel_export,
    personnel_batch_delete
)
from .views.views_notice import (
    notice_list, notice_add, notice_edit, notice_delete, notice_detail,
    notice_file_download, notice_file_preview
)
from .views.views_file_manage import (
    file_list, file_add, file_edit, file_delete,
    file_detail, file_download, file_preview
)
from .views.views_monthly_report import (
    monthly_report_list, monthly_report_create, monthly_report_edit,
    monthly_report_submit, monthly_report_detail, monthly_report_dashboard,
    get_pending_reports, clear_reminder
)
from .views.views_deploy import deploy_to_server, get_deploy_progress

try:
    from eims_app.views.debug_import import debug_import
except ImportError:
    debug_import = None
from .views.views_department import (
    department_list, department_detail, 
    department_edit, department_delete, department_role_list,
    approval_chain_list, approval_chain_create, approval_chain_edit, approval_chain_delete,
    organization_navigation, temp_welcome, department_create,
    department_role_create, department_role_edit, department_role_delete,
    add_role_type
)
from .views.views_file_manage import (
    file_list, file_add, file_detail, 
    file_edit, file_delete, file_download, file_preview
)
from .views import views_notice
from .views.views_monthly_report import (
    monthly_report_list, monthly_report_create, monthly_report_edit,
    monthly_report_submit, monthly_report_detail, monthly_report_dashboard,
    get_pending_reports, clear_reminder
)
from .views.views_monthly_report_reminder import get_monthly_report_reminders
from .views.views_workflow import (
    approval_flow_list, approval_flow_detail, submit_for_review,
    director_review, admin_approval, my_pending_reviews
)
from .views.views_attachments import (
    office_online_preview, notice_batch_upload, notice_batch_upload_page,
    file_manage_batch_upload, file_manage_batch_upload_page,
    create_new_version, delete_version, set_file_permission
)
from .views.views_dynamic_choice import (
    add_dynamic_choice, get_dynamic_choices, manage_dynamic_choice
)
from .views import views_project_ledger, views_contract_management
from .views import views_cost_sub_modules
from .views.views_sms_auth import (
    send_sms_code, sms_login, change_phone, reset_password_by_sms
)
from .views.views_forgot_password import (
    forgot_password_page, send_forgot_password_code, verify_and_reset_password
)
from .views.views_user_management import (
    user_management, sync_user_from_employee
)
from .views.views_qr_login import (
    qr_login_page, qr_login_scan, qr_login_confirm,
    qr_login_status, qr_login_complete, qr_login_cancel
)
from .views.views_wechat_login import (
    wechat_qr_login_page, wechat_login_callback,
    wechat_bind_account, wechat_check_status,
    wechat_unbind, wechat_my_bindings
)
from .views.views_tenant import tenant_select, tenant_switch, tenant_list
from .views.views_user_management import user_management, sync_user_from_employee
from django.views.generic import RedirectView

# 导入调试工具（临时使用）
try:
    import sys
    import os
    # 添加项目根目录到 Python 路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from debug_import_tool import debug_import
except ImportError:
    debug_import = None

app_name = 'eims_app'

urlpatterns = [
    # 首页
    path('', views_cost_sub_modules.cost_project_info_list, name='eims_index'),
    path('system/navigation/', system_navigation, name='system_navigation'),
    
    # 工程业务模块路由（待开发）
    path('module/preparation/', module_welcome, {'module_name': '前期准备'}, name='module_preparation'),
    path('module/bidding/', module_welcome, {'module_name': '招标投标'}, name='module_bidding'),
    path('module/design/', module_welcome, {'module_name': '工程设计'}, name='module_design'),
    path('module/cost/', module_welcome, {'module_name': '造价咨询'}, name='module_cost'),
    path('module/construction/', module_welcome, {'module_name': '工程施工'}, name='module_construction'),
    path('module/testing/', module_welcome, {'module_name': '工程检测'}, name='module_testing'),
    
    # 租户（公司）选择路由
    path('tenant/select/', tenant_select, name='tenant_select'),
    path('tenant/switch/', tenant_switch, name='tenant_switch'),
    
    # 租户（公司）管理路由 - Root超级管理员专属
    path('tenants/', tenant_list, name='tenant_list'),
    
    # 用户管理路由 - Root超级管理员专属
    path('users/', user_management, name='user_management'),
    path('users/sync/<int:employee_id>/', sync_user_from_employee, name='sync_user_from_employee'),
    
    # 项目管理路由
    path('contract/contract/', RedirectView.as_view(url='/contract/', permanent=True)),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/add/', ProjectCreateView.as_view(), name='project_add'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    # 旧的项目详情页已废弃，重定向到新的项目台账详情页
    path('projects/<int:pk>/', RedirectView.as_view(url='/project_ledger/%(pk)s/', permanent=False), name='project_redirect'),
    path('projects/<int:pk>/import-dynamic/', import_project_dynamic, name='import_project_dynamic'),
    path('projects/<int:pk>/import-output/', import_output_payment, name='import_output_payment'),
    path('projects/<int:pk>/import-personnel/', import_personnel, name='import_personnel'),
    path('projects/<int:pk>/delete-dynamic/', delete_dynamic, name='delete_dynamic'),
    path('projects/<int:pk>/delete-output/', delete_output, name='delete_output'),
    path('projects/<int:pk>/delete-personnel/', delete_personnel, name='delete_personnel'),
    # 新增页面路由
    path('project_ledger/<int:pk>/add-dynamic/', add_dynamic, name='add_dynamic'),
    path('project_ledger/<int:pk>/add-output/', add_output, name='add_output'),
    path('project_ledger/<int:pk>/add-personnel/', add_personnel, name='add_personnel'),
    path('projects/batch-delete/', project_batch_delete, name='project_batch_delete'),
    path('projects/export/', project_export, name='project_export'),
    path('projects/import/', project_import, name='project_import'),
    path('api/project-by-contract/', project_by_contract, name='project_by_contract'),
    
    # 合同管理路由
    path('contract/', contract_list, name='contract_list'),
    path('contract/add/', contract_add, name='contract_add'),
    path('contract/<int:pk>/edit/', contract_edit, name='contract_edit'),
    path('contract/<int:pk>/delete/', contract_delete, name='contract_delete'),
    path('contract/<int:pk>/', contract_detail, name='contract_detail'),
    path('contract/batch-delete/', contract_batch_delete, name='contract_batch_delete'),
    path('contract/import/', contract_import, name='contract_import'),
    path('contract/export/', contract_export, name='contract_export'),
    path('contract-approval/', contract_approval_chain, name='contract_approval_chain'),
    path('contract-approval/add/', contract_approval_add, name='contract_approval_add'),
    path('contract-approval/<int:pk>/', contract_approval_detail, name='contract_approval_detail'),
    path('contract-approval/<int:pk>/edit/', contract_approval_edit, name='contract_approval_edit'),
    path('contract-approval/<int:pk>/submit/', contract_approval_submit, name='contract_approval_submit'),
    path('contract-approval/<int:pk>/approve/', contract_approval_approve, name='contract_approval_approve'),
    path('contract-approval/<int:pk>/reject/', contract_approval_reject, name='contract_approval_reject'),
    path('contract-approval/<int:pk>/cancel/', contract_approval_cancel, name='contract_approval_cancel'),
    # 归档审批路由
    path('archive-approval/', archive_approval_chain, name='archive_approval_chain'),
    path('archive-approval/add/', archive_approval_add, name='archive_approval_add'),
    path('archive-approval/<int:pk>/', archive_approval_detail, name='archive_approval_detail'),
    path('archive-approval/<int:pk>/edit/', archive_approval_edit, name='archive_approval_edit'),
    path('archive-approval/<int:pk>/submit/', archive_approval_submit, name='archive_approval_submit'),
    path('archive-approval/<int:pk>/approve/', archive_approval_approve, name='archive_approval_approve'),
    path('archive-approval/<int:pk>/reject/', archive_approval_reject, name='archive_approval_reject'),
    path('archive-approval/<int:pk>/cancel/', archive_approval_cancel, name='archive_approval_cancel'),
    # 用印审批路由
    path('seal-approval/', seal_approval_list, name='seal_approval_chain'),
    path('seal-approval/add/', seal_approval_add, name='seal_approval_add'),
    path('seal-approval/<int:pk>/', seal_approval_detail, name='seal_approval_detail'),
    path('seal-approval/<int:pk>/edit/', seal_approval_edit, name='seal_approval_edit'),
    path('seal-approval/<int:pk>/submit/', seal_approval_submit, name='seal_approval_submit'),
    path('seal-approval/<int:pk>/approve/', seal_approval_approve, name='seal_approval_approve'),
    path('seal-approval/<int:pk>/reject/', seal_approval_reject, name='seal_approval_reject'),
    path('seal-approval/<int:pk>/cancel/', seal_approval_cancel, name='seal_approval_cancel'),
    path('seal-approval/attachment/<int:attachment_id>/delete/', seal_approval_delete_attachment, name='seal_approval_delete_attachment'),
    path('seal-approval/attachment/<int:attachment_id>/preview/', seal_attachment_preview, name='seal_attachment_preview'),
    path('seal-approval/attachment/<int:attachment_id>/download/', seal_attachment_download, name='seal_attachment_download'),
    path('seal-approval/get-department-personnel/', get_department_personnel_ajax, name='get_department_personnel_ajax'),
    path('my-pending-approvals/', my_pending_approvals, name='my_pending_approvals'),
    path('my-initiated-approvals/', my_initiated_approvals, name='my_initiated_approvals'),
    path('contract/import/template/', contract_import_template, name='contract_import_template'),
    path('contract/export/', contract_export, name='contract_export'),
    
    # 个人设置路由
    path('profile/', profile_view, name='profile'),
    path('my-account/', my_account_view, name='my_account'),
    
    # 人员管理路由
    path('employee/', employee_list, name='employee_list'),
    path('employee/add/', employee_add, name='employee_add'),
    path('employee/<int:pk>/', employee_detail, name='employee_detail'),
    path('employee/<int:pk>/edit/', employee_edit, name='employee_edit'),
    path('employee/<int:pk>/delete/', employee_delete, name='employee_delete'),
    path('employee/batch-delete/', employee_batch_delete, name='employee_batch_delete'),
    path('employee/export/', employee_export, name='employee_export'),
    
    path('personnel/', views_personnel.personnel_list, name='personnel_list'),
    path('personnel/list/', views_personnel.personnel_list, name='personnel_list_full'),
    path('personnel/navigation/', views_personnel.personnel_navigation, name='personnel_navigation'),
    path('personnel/add/', views_personnel.personnel_add, name='personnel_add'),
    path('personnel/destination/', views_personnel.personnel_destination, name='personnel_destination'),
    path('personnel/import/', views_personnel.personnel_import, name='personnel_import'),
    path('personnel/import/template/', views_personnel.personnel_import_template, name='personnel_import_template'),
    path('personnel/export/', views_personnel.personnel_export, name='personnel_export'),
    path('personnel/batch-delete/', views_personnel.personnel_batch_delete, name='personnel_batch_delete'),
    path('personnel/<int:pk>/', views_personnel.personnel_detail, name='personnel_detail'),
    path('personnel/<int:pk>/edit/', views_personnel.personnel_edit, name='personnel_edit'),
    path('personnel/<int:pk>/delete/', views_personnel.personnel_delete, name='personnel_delete'),
    
    # 文件管理路由
    path('file_manage/', file_list, name='file_manage_list'),
    path('file_manage/add/', file_add, name='file_manage_add'),
    path('file_manage/<int:file_id>/', file_detail, name='file_manage_detail'),
    path('file_manage/<int:file_id>/edit/', file_edit, name='file_manage_edit'),
    path('file_manage/<int:file_id>/delete/', file_delete, name='file_manage_delete'),
    path('file_manage/<int:file_id>/download/', file_download, name='file_manage_download'),
    path('file_manage/<int:file_id>/preview/', file_preview, name='file_manage_preview'),
    
    # 通知公告路由
    path('notice/', views_notice.notice_list, name='notice_list'),
    
    # 月度报告路由
    path('monthly-report/', monthly_report_list, name='monthly_report_list'),
    path('monthly-report/add/', monthly_report_create, name='monthly_report_add'),
    path('monthly-report/<int:pk>/edit/', monthly_report_edit, name='monthly_report_edit'),
    path('monthly-report/<int:pk>/submit/', monthly_report_submit, name='monthly_report_submit'),
    path('monthly-report/<int:pk>/', monthly_report_detail, name='monthly_report_detail'),
    path('monthly-report/dashboard/', monthly_report_dashboard, name='monthly_report_dashboard'),
    
    # 月度报告提醒 API
    path('api/monthly-report/pending/', get_pending_reports, name='get_pending_reports'),
    path('api/monthly-report/clear-reminder/', clear_reminder, name='clear_reminder'),
    path('api/monthly-report/reminders/', get_monthly_report_reminders, name='get_monthly_report_reminders'),
    
    # 审批流程路由
    path('workflow/', approval_flow_list, name='approval_flow_list'),
    path('workflow/<int:pk>/', approval_flow_detail, name='approval_flow_detail'),
    path('workflow/submit/<int:report_id>/', submit_for_review, name='submit_for_review'),
    path('workflow/<int:flow_id>/director-review/', director_review, name='director_review'),
    path('workflow/<int:flow_id>/admin-approval/', admin_approval, name='admin_approval'),
    path('workflow/my-pending/', my_pending_reviews, name='my_pending_reviews'),
    
    # 产值回款路由
    path('output_payment/', OutputPaymentListView.as_view(), name='output_payment_list'),
    path('output_payment/add/', OutputPaymentCreateView.as_view(), name='output_payment_add'),
    path('output_payment/<int:pk>/', OutputPaymentDetailView.as_view(), name='output_payment_detail'),
    path('output_payment/<int:pk>/edit/', OutputPaymentUpdateView.as_view(), name='output_payment_edit'),
    
    # 人员证书管理路由
    path('personnel/certificates/', certificate_list, name='certificate_list'),
    path('personnel/certificates/add/', certificate_create, name='certificate_add'),
    path('personnel/certificates/<int:pk>/', certificate_detail, name='certificate_detail'),
    path('personnel/certificates/<int:pk>/edit/', certificate_edit, name='certificate_edit'),
    path('personnel/certificates/<int:pk>/delete/', certificate_delete, name='certificate_delete'),
    
    # 人员分配管理路由
    path('personnel/allocations/', allocation_list, name='allocation_list'),
    path('personnel/allocations/add/', allocation_create, name='allocation_add'),
    path('personnel/allocations/<int:pk>/', allocation_detail, name='allocation_detail'),
    path('personnel/allocations/<int:pk>/edit/', allocation_edit, name='allocation_edit'),
    path('personnel/allocations/<int:pk>/delete/', allocation_delete, name='allocation_delete'),
    
    # 可视化人员分配路由
    path('personnel/allocation-visual/', allocation_visual, name='allocation_visual'),
    path('personnel/allocations/allocate-ajax/', allocate_personnel_ajax, name='allocate_personnel_ajax'),
    path('personnel/allocations/assign-department-ajax/', assign_to_department_ajax, name='assign_to_department_ajax'),
    path('personnel/allocations/recall/<int:pk>/', recall_personnel_ajax, name='recall_personnel_ajax'),
    path('personnel/allocations/update/<int:pk>/', update_personnel_allocation, name='update_personnel_allocation'),
    path('personnel/allocations/delete-all/<int:pk>/', delete_all_personnel_allocation, name='delete_all_personnel_allocation'),
    path('personnel/allocations/get-personnel-projects/<int:pk>/', get_personnel_projects, name='get_personnel_projects'),
    
    # 人员分配 AJAX 路由
    path('personnel/allocate-to-project-ajax/', allocate_to_project_ajax, name='allocate_to_project_ajax'),
    path('personnel/recall-to-company-ajax/', recall_to_company_ajax, name='recall_to_company_ajax'),
    path('personnel/recall-to-department-ajax/', recall_to_department_ajax, name='recall_to_department_ajax'),
    
    # 部门管理路由
    path('departments/', department_list, name='department_list'),
    path('departments/navigation/', organization_navigation, name='organization_navigation'),
    path('departments/welcome/', temp_welcome, name='department_welcome'),
    path('departments/add/', department_create, name='department_add'),
    path('departments/<int:pk>/', department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', department_delete, name='department_delete'),
    
    # 部门角色路由
    path('department-roles/', department_role_list, name='department_role_list'),
    path('department-roles/add/', department_role_create, name='department_role_add'),
    path('department-roles/<int:pk>/edit/', department_role_edit, name='department_role_edit'),
    path('department-roles/<int:pk>/delete/', department_role_delete, name='department_role_delete'),
    path('api/add-role-type/', add_role_type, name='add_role_type'),
    
    # 审批链路由
    path('approval-chains/', approval_chain_list, name='approval_chain_list'),
    path('approval-chains/add/', approval_chain_create, name='approval_chain_add'),
    path('approval-chains/<int:pk>/edit/', approval_chain_edit, name='approval_chain_edit'),
    path('approval-chains/<int:pk>/delete/', approval_chain_delete, name='approval_chain_delete'),
    
    # 动态选项管理路由
    path('api/dynamic-choices/add/', add_dynamic_choice, name='add_dynamic_choice'),
    path('api/dynamic-choices/<str:category>/', get_dynamic_choices, name='get_dynamic_choices'),
    path('api/dynamic-choices/manage/<int:pk>/', manage_dynamic_choice, name='manage_dynamic_choice'),
    
    # 通知公告路由
    path('notice/list/', views_notice.notice_list, name='notice_list'),
    path('notice/add/', views_notice.notice_add, name='notice_add'),
    path('notice/<int:pk>/add/', views_notice.notice_add, name='notice_add_with_id'),
    path('notice/<int:pk>/', views_notice.notice_detail, name='notice_detail'),
    path('notice/<int:pk>/edit/', views_notice.notice_edit, name='notice_edit'),
    path('notice/<int:pk>/delete/', views_notice.notice_delete, name='notice_delete'),
    path('notice/<int:pk>/file/download/', views_notice.notice_file_download, name='notice_file_download'),
    path('notice/<int:pk>/file/preview/', views_notice.notice_file_preview, name='notice_file_preview'),
    path('notice/batch-upload-page/', notice_batch_upload_page, name='notice_batch_upload_page'),
    
    # 附件管理路由
    path('notice/batch-upload/', notice_batch_upload, name='notice_batch_upload'),
    path('attachments/office-preview/', office_online_preview, name='office_online_preview'),
    path('attachments/<int:attachment_id>/office-preview/', office_online_preview, name='attachment_office_preview'),
    path('versions/<int:file_version_id>/office-preview/', office_online_preview, name='version_office_preview'),
    path('versions/create/<int:pk>/<str:module_type>/', create_new_version, name='create_new_version'),
    path('versions/delete/<int:version_id>/<str:module_type>/', delete_version, name='delete_version'),
    
    # 文件管理路由
    path('file-manage/batch-upload/', file_manage_batch_upload, name='file_manage_batch_upload'),
    path('file-manage/batch-upload-page/', file_manage_batch_upload_page, name='file_manage_batch_upload_page'),
    
    # 权限管理路由
    path('permissions/set-file-permission/<int:user_id>/', set_file_permission, name='set_file_permission'),
    
    # 项目台账路由
    path('project_ledger/', views_project_ledger.project_ledger_list, name='project_ledger_list'),
    path('project_ledger/add/', views_project_ledger.project_ledger_add, name='project_ledger_add'),
    path('project_ledger/<int:pk>/', views_project_ledger.project_ledger_detail, name='project_ledger_detail'),
    path('project_ledger/<int:pk>/edit/', views_project_ledger.project_ledger_edit, name='project_ledger_edit'),
    path('project_ledger/<int:pk>/delete/', views_project_ledger.project_ledger_delete, name='project_ledger_delete'),
    path('project_ledger/import/', views_project_ledger.project_ledger_import, name='project_ledger_import'),
    path('project_ledger/export/', views_project_ledger.project_ledger_export, name='project_ledger_export'),
    path('project_ledger/batch_delete/', views_project_ledger.project_ledger_batch_delete, name='project_ledger_batch_delete'),
    path('project_ledger/<int:pk>/preview-contract/', views_project_ledger.preview_contract_text, name='preview_contract'),
    path('project_ledger/<int:pk>/preview-permit/', views_project_ledger.preview_construction_permit, name='preview_permit'),
    path('project_ledger/<int:pk>/preview-notice/', views_project_ledger.preview_entry_notice, name='preview_notice'),
    
    # 项目搜索路由
    path('project_search/', views_project_ledger.project_search, name='project_search'),
    
    # 项目搜索 API 路由（用于 AJAX 搜索）
    path('api/projects/search/', views_project_ledger.project_search_api, name='project_search_api'),
    
    # 合同管理路由
    path('contract_management/', views_contract_management.contract_management_list, name='contract_management_list'),
    path('contract_management/add/', views_contract_management.contract_management_add, name='contract_management_add'),
    path('contract_management/<int:pk>/', views_contract_management.contract_management_detail, name='contract_management_detail'),
    path('contract_management/<int:pk>/edit/', views_contract_management.contract_management_edit, name='contract_management_edit'),
    path('contract_management/<int:pk>/delete/', views_contract_management.contract_management_delete, name='contract_management_delete'),
    path('contract_management/import/', views_contract_management.contract_management_import, name='contract_management_import'),
    path('contract_management/export/', views_contract_management.contract_management_export, name='contract_management_export'),
    path('contract_management/batch_delete/', views_contract_management.contract_management_batch_delete, name='contract_management_batch_delete'),
    path('contract_management/<int:pk>/preview-contract/', views_contract_management.preview_contract_text_contract, name='preview_contract_contract'),
    
    # 造价咨询 - 项目信息子模块路由
    path('cost_project_info/', views_cost_sub_modules.cost_project_info_list, name='cost_project_info_list'),
    path('cost_project_info/add/', views_cost_sub_modules.cost_project_info_add, name='cost_project_info_add'),
    path('cost_project_info/<int:pk>/', views_cost_sub_modules.cost_project_info_detail, name='cost_project_info_detail'),
    path('cost_project_info/<int:pk>/edit/', views_cost_sub_modules.cost_project_info_edit, name='cost_project_info_edit'),
    path('cost_project_info/<int:pk>/delete/', views_cost_sub_modules.cost_project_info_delete, name='cost_project_info_delete'),
    path('cost_project_info/batch-delete/', views_cost_sub_modules.cost_project_info_batch_delete, name='cost_project_info_batch_delete'),
    path('cost_project_info/export/', views_cost_sub_modules.cost_project_info_export, name='cost_project_info_export'),
    path('cost_project_info/import/', views_cost_sub_modules.cost_project_info_import, name='cost_project_info_import'),
    path('cost_project_info/export-template/', views_cost_sub_modules.cost_project_info_export_template, name='cost_project_info_export_template'),
    # API 路由
    path('api/cost-project-info/<int:pk>/', views_cost_sub_modules.cost_project_info_api, name='cost_project_info_api'),
    
    # 造价咨询 - 任务计划子模块路由
    path('cost_task_plan/', views_cost_sub_modules.cost_task_plan_list, name='cost_task_plan_list'),
    path('cost_task_plan/add/', views_cost_sub_modules.cost_task_plan_add, name='cost_task_plan_add'),
    path('cost_task_plan/<int:pk>/', views_cost_sub_modules.cost_task_plan_detail, name='cost_task_plan_detail'),
    path('cost_task_plan/<int:pk>/edit/', views_cost_sub_modules.cost_task_plan_edit, name='cost_task_plan_edit'),
    path('cost_task_plan/<int:pk>/delete/', views_cost_sub_modules.cost_task_plan_delete, name='cost_task_plan_delete'),
    path('cost_task_plan/batch-delete/', views_cost_sub_modules.cost_task_plan_batch_delete, name='cost_task_plan_batch_delete'),
    path('cost_task_plan/export/', views_cost_sub_modules.cost_task_plan_export, name='cost_task_plan_export'),
    
    # 造价咨询 - 任务实施子模块路由
    path('cost_task_implementation/', views_cost_sub_modules.cost_task_implementation_list, name='cost_task_implementation_list'),
    path('cost_task_implementation/add/', views_cost_sub_modules.cost_task_implementation_add, name='cost_task_implementation_add'),
    path('cost_task_implementation/<int:pk>/', views_cost_sub_modules.cost_task_implementation_detail, name='cost_task_implementation_detail'),
    path('cost_task_implementation/<int:pk>/edit/', views_cost_sub_modules.cost_task_implementation_edit, name='cost_task_implementation_edit'),
    path('cost_task_implementation/<int:pk>/delete/', views_cost_sub_modules.cost_task_implementation_delete, name='cost_task_implementation_delete'),
    path('cost_task_implementation/batch-delete/', views_cost_sub_modules.cost_task_implementation_batch_delete, name='cost_task_implementation_batch_delete'),
    path('cost_task_implementation/export/', views_cost_sub_modules.cost_task_implementation_export, name='cost_task_implementation_export'),
    
    # 造价咨询 - 审核成果子模块路由
    path('cost_review_result/', views_cost_sub_modules.cost_review_result_list, name='cost_review_result_list'),
    path('cost_review_result/add/', views_cost_sub_modules.cost_review_result_add, name='cost_review_result_add'),
    path('cost_review_result/<int:pk>/', views_cost_sub_modules.cost_review_result_detail, name='cost_review_result_detail'),
    path('cost_review_result/<int:pk>/edit/', views_cost_sub_modules.cost_review_result_edit, name='cost_review_result_edit'),
    path('cost_review_result/<int:pk>/delete/', views_cost_sub_modules.cost_review_result_delete, name='cost_review_result_delete'),
    path('cost_review_result/batch-delete/', views_cost_sub_modules.cost_review_result_batch_delete, name='cost_review_result_batch_delete'),
    path('cost_review_result/export/', views_cost_sub_modules.cost_review_result_export, name='cost_review_result_export'),
    
    # 造价咨询 - 收费情况子模块路由
    path('cost_payment_status/', views_cost_sub_modules.cost_payment_status_list, name='cost_payment_status_list'),
    path('cost_payment_status/add/', views_cost_sub_modules.cost_payment_status_add, name='cost_payment_status_add'),
    path('cost_payment_status/<int:pk>/', views_cost_sub_modules.cost_payment_status_detail, name='cost_payment_status_detail'),
    path('cost_payment_status/<int:pk>/edit/', views_cost_sub_modules.cost_payment_status_edit, name='cost_payment_status_edit'),
    path('cost_payment_status/<int:pk>/delete/', views_cost_sub_modules.cost_payment_status_delete, name='cost_payment_status_delete'),
    path('cost_payment_status/batch-delete/', views_cost_sub_modules.cost_payment_status_batch_delete, name='cost_payment_status_batch_delete'),
    path('cost_payment_status/export/', views_cost_sub_modules.cost_payment_status_export, name='cost_payment_status_export'),
    
    # 造价咨询 - 项目存档子模块路由
    path('cost_project_archive/', views_cost_sub_modules.cost_project_archive_list, name='cost_project_archive_list'),
    path('cost_project_archive/add/', views_cost_sub_modules.cost_project_archive_add, name='cost_project_archive_add'),
    path('cost_project_archive/<int:pk>/', views_cost_sub_modules.cost_project_archive_detail, name='cost_project_archive_detail'),
    path('cost_project_archive/<int:pk>/edit/', views_cost_sub_modules.cost_project_archive_edit, name='cost_project_archive_edit'),
    path('cost_project_archive/<int:pk>/delete/', views_cost_sub_modules.cost_project_archive_delete, name='cost_project_archive_delete'),
    path('cost_project_archive/batch-delete/', views_cost_sub_modules.cost_project_archive_batch_delete, name='cost_project_archive_batch_delete'),
    path('cost_project_archive/export/', views_cost_sub_modules.cost_project_archive_export, name='cost_project_archive_export'),
    
    # 造价咨询 - 酬劳分配子模块路由
    path('cost_remuneration_distribution/', views_cost_sub_modules.cost_remuneration_distribution_list, name='cost_remuneration_distribution_list'),
    path('cost_remuneration_distribution/add/', views_cost_sub_modules.cost_remuneration_distribution_add, name='cost_remuneration_distribution_add'),
    path('cost_remuneration_distribution/<int:pk>/', views_cost_sub_modules.cost_remuneration_distribution_detail, name='cost_remuneration_distribution_detail'),
    path('cost_remuneration_distribution/<int:pk>/edit/', views_cost_sub_modules.cost_remuneration_distribution_edit, name='cost_remuneration_distribution_edit'),
    path('cost_remuneration_distribution/<int:pk>/delete/', views_cost_sub_modules.cost_remuneration_distribution_delete, name='cost_remuneration_distribution_delete'),
    path('cost_remuneration_distribution/batch-delete/', views_cost_sub_modules.cost_remuneration_distribution_batch_delete, name='cost_remuneration_distribution_batch_delete'),
    path('cost_remuneration_distribution/export/', views_cost_sub_modules.cost_remuneration_distribution_export, name='cost_remuneration_distribution_export'),
    
    # 造价咨询 - 提醒通知路由
    path('api/cost-reminders/unread-count/', views_cost_sub_modules.get_unread_reminder_count, name='get_unread_reminder_count'),
    path('api/cost-reminders/mark-read/<int:pk>/', views_cost_sub_modules.mark_reminder_read, name='mark_reminder_read'),
    path('api/cost-reminders/snooze/', views_cost_sub_modules.snooze_reminder, name='snooze_reminder'),
    path('api/cost-reminders/ignore/', views_cost_sub_modules.ignore_reminder, name='ignore_reminder'),
    
    # 短信认证相关路由
    path('api/sms/send-code/', send_sms_code, name='send_sms_code'),
    path('api/sms/login/', sms_login, name='sms_login'),
    path('api/sms/change-phone/', change_phone, name='change_phone'),
    path('api/sms/reset-password/', reset_password_by_sms, name='reset_password_by_sms'),
    
    # 忘记密码相关路由
    path('forgot-password/', forgot_password_page, name='forgot_password'),
    path('api/forgot-password/send-code/', send_forgot_password_code, name='send_forgot_password_code'),
    path('api/forgot-password/verify-reset/', verify_and_reset_password, name='verify_and_reset_password'),
    
    # 用户账号管理路由
    path('user-management/', user_management, name='user_management'),
    path('user-management/sync/<int:employee_id>/', sync_user_from_employee, name='sync_user_from_employee'),
    
    # 二维码登录路由
    path('qr-login/', qr_login_page, name='qr_login_page'),
    path('qr-login/scan/<uuid:session_id>/', qr_login_scan, name='qr_login_scan'),
    path('qr-login/confirm/', qr_login_confirm, name='qr_login_confirm'),
    path('qr-login/status/<uuid:session_id>/', qr_login_status, name='qr_login_status'),
    path('qr-login/complete/<uuid:session_id>/', qr_login_complete, name='qr_login_complete'),
    path('qr-login/cancel/', qr_login_cancel, name='qr_login_cancel'),
    
    # 微信扫码登录路由（真正的微信开放平台集成）
    path('wechat-login/', wechat_qr_login_page, name='wechat_qr_login'),
    path('wechat-login/callback/', wechat_login_callback, name='wechat_login_callback'),
    path('wechat-login/bind/', wechat_bind_account, name='wechat_bind_account'),
    path('wechat-login/status/<uuid:session_id>/', wechat_check_status, name='wechat_check_status'),
    path('wechat-login/unbind/', wechat_unbind, name='wechat_unbind'),
    path('wechat-login/my-bindings/', wechat_my_bindings, name='wechat_my_bindings'),
    
    # 部署相关路由
    path('api/deploy/', deploy_to_server, name='deploy_to_server'),
    path('api/deploy/progress/<str:task_id>/', get_deploy_progress, name='get_deploy_progress'),
]

# 调试工具路由（仅在开发环境使用）
if debug_import:
    urlpatterns.append(
        path('debug_import/', debug_import, name='debug_import')
    )
