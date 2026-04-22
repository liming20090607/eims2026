from django import forms
from eims_app.models.model_seal_approval import SealApproval, SealAttachment
from eims_app.models.model_department import Department
from eims_app.models.model_approval_flow import DepartmentManager
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class SealApprovalForm(forms.ModelForm):
    """用印审批表单"""
    
    # 部门字段使用 ModelChoiceField，自动从 Department 模型加载
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_deleted=False),
        required=False,
        empty_label="请选择部门",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # 审批流程类型
    approval_flow_type = forms.ChoiceField(
        label="审批流程类型",
        choices=SealApproval.APPROVAL_FLOW_TYPE_CHOICES,
        required=True,
        initial='user_selected',  # 默认为"由我选择审批人"
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    # 用户选择的审批部门
    selected_department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_deleted=False),
        required=False,
        empty_label="请选择审批部门",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_selected_department'
        })
    )
    
    # 用户选择的审批人
    selected_approver = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="请选择审批人",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_selected_approver'
        })
    )
    
    class Meta:
        model = SealApproval
        fields = [
            'title', 'department', 'approval_flow_type', 'selected_department', 'selected_approver',
            'seal_type', 'seal_count', 'document_name', 'document_type',
            'project_name', 'project_code', 'usage_purpose', 'remark'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入审批标题'
            }),
            'seal_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seal_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '请输入盖章数量'
            }),
            'document_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入文件名称'
            }),
            'document_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：合同、报告、证明等'
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入关联项目名称（可选）'
            }),
            'project_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目编号（可选）'
            }),
            'usage_purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请说明用印的具体用途'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入备注信息'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """初始化表单，根据选择的部门过滤审批人"""
        super().__init__(*args, **kwargs)
        
        # 如果编辑已有对象，设置初始值
        if self.instance and self.instance.pk:
            self.fields['approval_flow_type'].initial = self.instance.approval_flow_type
            self.fields['selected_department'].initial = self.instance.selected_department
            self.fields['selected_approver'].initial = self.instance.selected_approver
    
    def clean_selected_approver(self):
        """验证选择的审批人"""
        selected_approver = self.cleaned_data.get('selected_approver')
        approval_flow_type = self.cleaned_data.get('approval_flow_type')
        
        # 如果是用户选择模式且没有选择审批人，提示错误
        if approval_flow_type == 'user_selected' and not selected_approver:
            # 但如果选择了部门，允许不选具体审批人（系统会从部门中找主管）
            if not self.cleaned_data.get('selected_department'):
                raise forms.ValidationError("请选择审批人或审批部门")
        
        return selected_approver


class SealAttachmentForm(forms.ModelForm):
    """用印附件上传表单"""
    
    class Meta:
        model = SealAttachment
        fields = ['file', 'file_type']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
