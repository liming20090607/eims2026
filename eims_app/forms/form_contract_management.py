from django import forms
from ..models import ProjectDetail


class ContractManagementForm(forms.ModelForm):
    """合同管理表单 - 用于合同管理模块的增删改"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 为下拉列表添加选项
        self.fields['contract_category'].choices = [
            ('', '请选择'),
            ('engineering_supervision', '工程监理'),
            ('cost_consulting', '造价咨询'),
            ('testing', '检测'),
            ('whole_process_consulting', '全过程咨询'),
            ('other', '其他（手动输入）'),
        ]
        
        self.fields['contract_status'].choices = [
            ('', '请选择'),
            ('pending_review', '待审核'),
            ('executing', '在执行'),
            ('terminated', '已终止'),
            ('released', '已解除'),
            ('other', '其他（手动输入）'),
        ]
        
        self.fields['settlement_status'].choices = [
            ('', '请选择'),
            ('unsettled', '未结算'),
            ('settled', '已结算'),
            ('other', '其他（手动输入）'),
        ]
        
        # 如果是新增实例（没有 PK），清空默认值
        if not self.instance.pk:
            self.initial['contract_category'] = ''
            self.initial['contract_status'] = ''
            self.initial['settlement_status'] = ''
        # 编辑现有记录时，ModelForm 会自动从 instance 加载数据，无需手动设置 initial
    
    class Meta:
        model = ProjectDetail
        fields = [
            'project_code', 'contract_code', 'contract_category', 'project_name',
            'contract_status', 'settlement_status',
            'contract_party_a', 'contract_party_b', 'signing_date',
            'contract_text', 'contract_amount', 'payment_agreement',
            'project_scale', 'project_investment', 'project_address',
            'agreed_staffing', 'service_start_date', 'service_period_months', 'service_deadline',
            'extension_agreement',
            'planned_start_date', 'estimated_completion_date',
            'remark',
        ]
        
        widgets = {
            # 项目编号
            'project_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目编号（唯一）'
            }),
            
            # 下拉选择 - 使用标准的 select 元素
            'contract_category': forms.Select(attrs={'class': 'form-select'}),
            'contract_status': forms.Select(attrs={'class': 'form-select'}),
            'settlement_status': forms.Select(attrs={'class': 'form-select'}),
            
            # 文本输入
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
                'type': 'month'  # 改为月份选择器，格式：YYYY-MM
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
            
            # 数字输入
            'contract_amount': forms.NumberInput(attrs={
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
            }, format='%Y-%m-%d'),
            'planned_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estimated_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'service_deadline': forms.DateInput(attrs={
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
    
    def clean_contract_code(self):
        """验证合同编号唯一性"""
        contract_code = self.cleaned_data.get('contract_code')
        if contract_code:
            # 排除当前记录（编辑时）
            queryset = ProjectDetail.objects.filter(contract_code=contract_code)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('合同编号已存在，请使用其他编号')
        return contract_code
    
    def clean(self):
        """保存前将中文状态值转换为英文存储"""
        cleaned_data = super().clean()
        
        # 中文到英文的映射
        category_reverse_map = {
            '工程监理': 'engineering_supervision',
            '造价咨询': 'cost_consulting',
            '检测': 'testing',
            '全过程咨询': 'whole_process_consulting',
        }
        contract_status_reverse_map = {
            '待审核': 'pending_review',
            '在执行': 'executing',
            '已终止': 'terminated',
            '已解除': 'released',
        }
        settlement_status_reverse_map = {
            '未结算': 'unsettled',
            '已结算': 'settled',
        }
        
        # 转换合同类别
        if cleaned_data.get('contract_category'):
            category = cleaned_data['contract_category']
            cleaned_data['contract_category'] = category_reverse_map.get(category, category)
        
        # 转换合同状态
        if cleaned_data.get('contract_status'):
            contract_status = cleaned_data['contract_status']
            cleaned_data['contract_status'] = contract_status_reverse_map.get(contract_status, contract_status)
        
        # 转换结算情况
        if cleaned_data.get('settlement_status'):
            settlement_status = cleaned_data['settlement_status']
            cleaned_data['settlement_status'] = settlement_status_reverse_map.get(settlement_status, settlement_status)
        
        return cleaned_data
    
    def clean_contract_amount(self):
        """验证合同金额"""
        amount = self.cleaned_data.get('contract_amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError('合同金额不能为负数')
        return amount
