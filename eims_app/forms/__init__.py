
# 导入所有表单，便于视图调用
from .form_contract import ContractForm
from .form_personnel import PersonnelForm
from .form_employee import EmployeeForm
from .form_project import ProjectForm
from .form_output_payment import OutputForm
from .form_file_manage import FileForm
from .form_notice import NoticeForm
from .form_personnel_detail import PersonnelCertificateForm, PersonnelAllocationForm
from .form_attachments import (
    NoticeAttachmentForm, NoticeBatchUploadForm,
    FileManageVersionForm, FileManageBatchUploadForm
)

__all__ = [
    'ContractForm', 'PersonnelForm', 'EmployeeForm', 'ProjectForm', 'OutputForm',
    'FileForm', 'NoticeForm',
    'PersonnelCertificateForm', 'PersonnelAllocationForm',
    'NoticeAttachmentForm', 'NoticeBatchUploadForm',
    'FileManageVersionForm', 'FileManageBatchUploadForm'
] 
