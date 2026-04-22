from django import forms
from eims_app.models.model_contract_approval import ContractApproval, ContractAttachment
from eims_app.models.model_department import Department
from eims_app.models.model_approval_flow import DepartmentManager
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class ContractApprovalForm(forms.ModelForm):
    """合同审批表单"""
    
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
        choices=ContractApproval.APPROVAL_FLOW_TYPE_CHOICES,
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
        model = ContractApproval
        fields = [
            'title', 'contract_name', 'contract_category', 'contract_amount',
            'department', 'approval_flow_type', 'selected_department', 'selected_approver',
            'party_a', 'party_b', 'service_start_date',
            'service_period_months', 'service_deadline', 'remark'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入审批标题'
            }),
            'contract_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入合同名称'
            }),
            'contract_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '请输入合同金额'
            }),
            'party_a': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入合同甲方'
            }),
            'party_b': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入合同乙方'
            }),
            'service_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'service_period_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '例如：12'
            }),
            'service_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly'  # 只读，自动计算
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


class ContractAttachmentForm(forms.ModelForm):
    """合同附件上传表单"""
    
    class Meta:
        model = ContractAttachment
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
