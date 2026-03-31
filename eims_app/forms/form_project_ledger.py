from django import forms
from ..models import ProjectDetail


class ProjectLedgerForm(forms.ModelForm):
    """项目台账表单 - 用于项目台账子模块的增删改"""
    
    # 将布尔字段转换为字符字段以支持下拉选择
    monthly_report_required = forms.ChoiceField(
        label='项目月报',
        choices=[
            ('', '请选择'),
            ('true', '是'),
            ('false', '否'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 编辑现有记录时，将布尔值转换为字符串
        if self.instance.pk and self.instance.monthly_report_required is not None:
            if self.instance.monthly_report_required is True:
                self.initial['monthly_report_required'] = 'true'
            elif self.instance.monthly_report_required is False:
                self.initial['monthly_report_required'] = 'false'
        
        self.fields['project_status'].choices = [
            ('', '请选择'),
            ('not_started', '未开工'),
            ('under_construction', '在施工'),
            ('stopped', '在停工'),
            ('completed', '已完工'),
            ('other', '其他（手动输入）'),
        ]
        
        self.fields['contract_status'].choices = [
            ('', '请选择'),
            ('pending_review', '审批中'),
            ('executing', '执行中'),
            ('released', '已解除'),
            ('suspended', '已中止'),
            ('terminated', '已终止'),
            ('other', '其他（手动输入）'),
        ]
        
        self.fields['construction_permit_status'].choices = [
            ('', '请选择'),
            ('not_started', '未办理'),
            ('in_progress', '办理中'),
            ('completed', '已办理'),
            ('other', '其他（手动输入）'),
        ]
        
        self.fields['entry_notice'].choices = [
            ('', '请选择'),
            ('no', '未提交'),
            ('submitted', '已提交'),
            ('approved', '已审批'),
            ('other', '其他（手动输入）'),
        ]
    
    class Meta:
        model = ProjectDetail
        fields = [
            'monthly_report_required', 'project_code', 'contract_code',
            'project_name', 'project_status', 'contract_status',
            'contract_party_a', 'contract_party_b', 'contract_text',
            'contract_amount', 'payment_agreement', 'cumulative_payment',
            'contract_balance', 'project_scale', 'project_investment',
            'project_address', 'agreed_staffing', 'service_start_date', 'service_period_months', 'service_deadline',
            'extension_agreement', 'actual_extension_status',
            'construction_permit_status', 'construction_permit',
            'entry_notice', 'entry_notice_document', 'entry_time',
            'actual_start_date', 'estimated_completion_date',
            'project_director', 'project_manager', 'contact_phone',
            'remark',
        ]
        
        widgets = {
            # 下拉选择 - 全部使用标准的 select 元素
            'monthly_report_required': forms.Select(attrs={'class': 'form-select'}),
            'project_status': forms.Select(attrs={'class': 'form-select'}),
            'contract_status': forms.Select(attrs={'class': 'form-select'}),
            'construction_permit_status': forms.Select(attrs={'class': 'form-select'}),
            'entry_notice': forms.Select(attrs={'class': 'form-select'}),
            
            # 文本输入
            'project_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目编号'
            }),
            'contract_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入合同编号'
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目名称'
            }),
            'contract_party_a': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入合同甲方'
            }),
            'contract_party_b': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入合同乙方'
            }),
            'project_scale': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：建筑面积 5 万㎡/道路长度 10km'
            }),
            'project_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目地址'
            }),
            'agreed_staffing': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '约定的人员配备情况'
            }),
            'service_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'  # Changed from 'month' to 'date' for full date selection
            }),
            'service_period_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '以月为单位'
            }),
            'extension_agreement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '延期约定'
            }),
            'actual_extension_status': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '实际延期情况'
            }),
            'project_director': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '项目总监姓名'
            }),
            'project_manager': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '现场负责人姓名'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系电话'
            }),
            
            # 数字输入
            'contract_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'cumulative_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'contract_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'project_investment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            
            # 日期选择
            'signing_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'service_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'entry_time': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'actual_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estimated_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            
            # 多行文本
            'payment_agreement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入付款约定'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入备注信息'
            }),
            
            # 文件上传
            'contract_text': forms.FileInput(attrs={'class': 'form-control'}),
            'construction_permit': forms.FileInput(attrs={'class': 'form-control'}),
            'entry_notice_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_project_code(self):
        """验证项目编号唯一性"""
        project_code = self.cleaned_data.get('project_code')
        if project_code:
            # 排除当前记录（编辑时）
            queryset = ProjectDetail.objects.filter(project_code=project_code)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('项目编号已存在，请使用其他编号')
        return project_code
    
    def clean(self):
        """保存前将中文状态值转换为英文存储"""
        cleaned_data = super().clean()
        
        # 中文到英文的映射
        status_reverse_map = {
            '未开工': 'not_started',
            '在施工': 'under_construction',
            '在停工': 'stopped',
            '已完工': 'completed',
        }
        contract_status_reverse_map = {
            '审批中': 'pending_review',
            '执行中': 'executing',
            '已解除': 'released',
            '已中止': 'suspended',
            '已终止': 'terminated',
        }
        permit_status_reverse_map = {
            '未办理': 'not_started',
            '办理中': 'in_progress',
            '已办理': 'completed',
        }
        entry_notice_reverse_map = {
            '未提交': 'no',
            '已提交': 'submitted',
            '已审批': 'approved',
        }
        
        # 转换项目状态
        if cleaned_data.get('project_status'):
            status = cleaned_data['project_status']
            cleaned_data['project_status'] = status_reverse_map.get(status, status)
        
        # 转换合同状态
        if cleaned_data.get('contract_status'):
            contract_status = cleaned_data['contract_status']
            cleaned_data['contract_status'] = contract_status_reverse_map.get(contract_status, contract_status)
        
        # 转换报建情况
        if cleaned_data.get('construction_permit_status'):
            permit_status = cleaned_data['construction_permit_status']
            cleaned_data['construction_permit_status'] = permit_status_reverse_map.get(permit_status, permit_status)
        
        # 转换进场通知
        if cleaned_data.get('entry_notice'):
            entry_notice = cleaned_data['entry_notice']
            cleaned_data['entry_notice'] = entry_notice_reverse_map.get(entry_notice, entry_notice)
        
        # 转换布尔值 - 项目月报
        monthly_report = cleaned_data.get('monthly_report_required')
        if monthly_report == 'true':
            cleaned_data['monthly_report_required'] = True
        elif monthly_report == 'false':
            cleaned_data['monthly_report_required'] = False
        else:
            # 如果为空或请选择，设置为 None
            cleaned_data['monthly_report_required'] = None
        
        return cleaned_data
    
    def clean_contract_code(self):
        """验证合同编号格式"""
        contract_code = self.cleaned_data.get('contract_code')
        if contract_code:
            # 可以添加合同编号的格式验证规则
            pass
        return contract_code
    
    def clean_contract_amount(self):
        """验证合同金额"""
        amount = self.cleaned_data.get('contract_amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError('合同金额不能为负数')
        return amount
