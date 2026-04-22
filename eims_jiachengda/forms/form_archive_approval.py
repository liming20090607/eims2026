from django import forms
from eims_app.models.model_archive_approval import ArchiveApproval, ArchiveAttachment
from eims_app.models.model_department import Department
from eims_app.models.model_approval_flow import DepartmentManager
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class ArchiveApprovalForm(forms.ModelForm):
    """归档审批表单"""
    
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
        choices=ArchiveApproval.APPROVAL_FLOW_TYPE_CHOICES,
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
        model = ArchiveApproval
        fields = [
            'title', 'project_name', 'project_code',
            'department', 'approval_flow_type', 'selected_department', 'selected_approver',
            'archive_date', 'archive_location', 'archive_period', 'remark'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入审批标题'
            }),
            'project_name': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_project_name'
            }),
            'project_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '选择项目名称后自动填入',
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'archive_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'archive_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：档案室A-03柜'
            }),
            'archive_period': forms.Select(attrs={
                'class': 'form-select'
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
        
        # 从 ProjectDetail 模型加载项目列表作为 project_name 的选项
        from eims_app.models.model_project_detail import ProjectDetail
        projects = ProjectDetail.objects.filter(
            project_name__isnull=False
        ).exclude(
            project_name=''
        ).order_by('project_code').values_list('project_code', 'project_name')
        
        # 构建选择列表：显示"项目名称 - 项目编号"
        project_choices = [('', '请选择项目名称')]
        project_choices.extend([
            (code, f"{name} ({code})")
            for code, name in projects if code and name
        ])
        
        self.fields['project_name'].choices = project_choices
        
        # 如果编辑已有对象，设置初始值
        if self.instance and self.instance.pk:
            self.fields['approval_flow_type'].initial = self.instance.approval_flow_type
            self.fields['selected_department'].initial = self.instance.selected_department
            self.fields['selected_approver'].initial = self.instance.selected_approver
            # 设置项目选择器的初始值
            if self.instance.project_code:
                self.fields['project_name'].initial = self.instance.project_code
    
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
    
    def clean_project_name(self):
        """验证项目名称选择，并自动填充项目编号"""
        project_code = self.cleaned_data.get('project_name')  # 此时 project_name 的值是 project_code
        
        if project_code:
            from eims_app.models.model_project_detail import ProjectDetail
            try:
                project = ProjectDetail.objects.get(project_code=project_code)
                # 保存项目名称和编号到 cleaned_data 供后续使用
                self._project_name_value = project.project_name
                self._project_code_value = project.project_code
            except ProjectDetail.DoesNotExist:
                raise forms.ValidationError("选择的项目不存在")
        else:
            self._project_name_value = ''
            self._project_code_value = ''
        
        return project_code
    
    def save(self, commit=True):
        """保存时自动设置项目名称和编号"""
        instance = super().save(commit=False)
        
        # 设置项目名称和编号
        if hasattr(self, '_project_name_value') and self._project_name_value:
            instance.project_name = self._project_name_value
            instance.project_code = self._project_code_value
        
        if commit:
            instance.save()
        
        return instance


class ArchiveAttachmentForm(forms.ModelForm):
    """归档附件上传表单"""
    
    class Meta:
        model = ArchiveAttachment
        fields = ['file', 'file_type', 'pages', 'document_date', 'remark']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.dwg,.zip,.rar'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '请输入页数'
            }),
            'document_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '备注说明'
            }),
        }
