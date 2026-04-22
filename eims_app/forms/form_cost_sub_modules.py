"""
造价咨询子模块表单 - 包含7个子模块的表单定义
"""
from django import forms
from ..models import (
    CostProjectInfo,
    CostTaskPlan,
    CostTaskImplementation,
    CostReviewResult,
    CostPaymentStatus,
    CostProjectArchive,
    CostRemunerationDistribution,
    CostRemunerationItem,
    CostProjectUnified,
)


class CostProjectInfoForm(forms.ModelForm):
    """造价咨询项目信息表单 - 旧模型（保留兼容）"""
    
    class Meta:
        model = CostProjectInfo
        fields = '__all__'
        widgets = {
            'project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.Select(attrs={'class': 'form-select'}),
            'compilation_category': forms.Select(attrs={'class': 'form-select'}),
            'review_category': forms.Select(attrs={'class': 'form-select'}),
            'project_status': forms.Select(attrs={'class': 'form-select'}),
            'client_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entrusting_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'submission_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'planned_completion_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'compilation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'submission_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approved_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reduced_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'report_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'result_confirm': forms.Select(attrs={'class': 'form-select'}),
            'total_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'received_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pending_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fee_settlement': forms.Select(attrs={'class': 'form-select'}),
        }


class CostProjectUnifiedForm(forms.ModelForm):
    """造价咨询项目信息表单 - 统一表模型"""
    
    # 项目负责人下拉列表 - 显示本公司员工花名册人员，按拼音首字母升序排列
    project_manager_personnel = forms.ModelChoiceField(
        queryset=None,  # 在 __init__ 中动态设置
        required=False,
        label="项目负责人",
        empty_label="请选择项目负责人",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        # 获取 tenant 参数（用于过滤人员）
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 自动设置项目编号前缀（新增模式）
        if not self.instance.pk and tenant:
            try:
                # 从 tenant 对象获取前缀，避免触发额外的数据库查询
                # 如果 tenant 是通过 request.tenant 设置的，应该已经加载了所有字段
                prefix = getattr(tenant, 'project_code_prefix', '')
                
                if prefix:
                    # 生成默认项目编号：前缀 + 序号
                    # 查询当前租户的最大序号
                    from ..models import CostProjectUnified
                    existing_projects = CostProjectUnified.objects.filter(
                        tenant=tenant,
                        project_code__startswith=prefix
                    )
                    
                    max_seq = 0
                    for proj in existing_projects:
                        code = proj.project_code
                        # 提取序号部分（前缀后面的数字）
                        try:
                            seq_part = code.replace(prefix, '').replace('-', '').replace('_', '')
                            if seq_part.isdigit():
                                seq = int(seq_part)
                                if seq > max_seq:
                                    max_seq = seq
                        except:
                            pass
                    
                    new_seq = max_seq + 1
                    default_code = f"{prefix}{new_seq:04d}"
                    self.fields['project_code'].initial = default_code
            except Exception as e:
                # 如果出现任何错误，不设置默认值，避免影响表单加载
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to auto-generate project code: {e}")
        
        # 动态设置项目负责人的 queryset
        from ..models import Personnel
        from pypinyin import lazy_pinyin
        
        if tenant:
            # 获取在岗人员
            personnel_qs = Personnel.objects.filter(
                tenant=tenant,
                leave_time__isnull=True  # 只显示在岗人员
            )
            
            # 按姓名拼音首字母排序（使用 pypinyin）
            personnel_list = sorted(
                list(personnel_qs),
                key=lambda p: lazy_pinyin(p.name) if p.name else ['']
            )
            
            # 自定义排序选项
            self.fields['project_manager_personnel'].queryset = Personnel.objects.filter(
                id__in=[p.id for p in personnel_list] if personnel_list else []
            )
            
            # 重写 widget 的 choices 以保持排序
            if personnel_list:
                self.fields['project_manager_personnel'].widget.choices = [
                    ('', self.fields['project_manager_personnel'].empty_label)
                ] + [
                    (p.id, f"{p.name} ({p.personnel_code})") for p in personnel_list
                ]
        else:
            self.fields['project_manager_personnel'].queryset = Personnel.objects.none()
    
    class Meta:
        model = CostProjectUnified
        # 只包含项目信息模块的字段，不包含其他6个子模块的字段
        fields = [
            # 基础信息
            'project_code', 'project_name', 'project_type',
            'compilation_category', 'review_category', 'project_status',
            # 项目相关方
            'client_unit', 'entrusting_unit', 'contact_person', 'contact_phone',
            'project_manager_personnel',
            # 时间节点
            'submission_time', 'start_time', 'planned_duration', 'planned_completion_time',
            # 金额信息
            'compilation_amount', 'submission_amount', 'approved_amount', 'reduced_amount',
            # 报告信息
            'report_time', 'completion_time', 'result_confirm',
            # 费用信息
            'total_fee', 'received_fee', 'pending_fee', 'fee_settlement',
            # 备注
            'remark',
        ]
        widgets = {
            'project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.Select(attrs={'class': 'form-select'}),
            'compilation_category': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '可选择或手动输入专业',
                'list': 'major-list'
            }),
            'review_category': forms.Select(attrs={'class': 'form-select'}, choices=[('', '---------')] + CostProjectUnified.REVIEW_CATEGORY_CHOICES),
            'project_status': forms.Select(attrs={'class': 'form-select'}),
            'client_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entrusting_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'project_manager_personnel': forms.Select(attrs={'class': 'form-select'}),
            'submission_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'planned_completion_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'compilation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'submission_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approved_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reduced_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'report_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completion_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'result_confirm': forms.Select(attrs={'class': 'form-select'}),
            'total_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'received_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pending_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fee_settlement': forms.Select(attrs={'class': 'form-select'}),
        }


class CostTaskPlanForm(forms.ModelForm):
    """造价咨询任务计划表单 - 旧模型（保留兼容）"""
    
    class Meta:
        model = CostTaskPlan
        fields = '__all__'
        widgets = {
            # 核心外键字段
            'project': forms.Select(attrs={'class': 'form-select'}),
            # 冗余字段（设置为只读，由系统自动填充）
            'project_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'style': 'background-color: #f8f9fa;'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'style': 'background-color: #f8f9fa;'}),
            'project_type': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),
            # Personnel外键字段
            'compiler_personnel': forms.Select(attrs={'class': 'form-select'}),
            'first_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'second_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'third_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            # 原有字段
            'compiler': forms.TextInput(attrs={'class': 'form-control'}),
            'compilation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'first_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'first_review_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'first_review_planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_review_planned_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'second_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'second_review_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'second_review_planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'second_review_planned_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'third_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'third_review_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'third_review_planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'third_review_planned_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CostTaskPlanUnifiedForm(forms.ModelForm):
    """造价咨询任务计划表单 - 统一表模型"""
    
    # 项目选择字段
    selected_project = forms.ModelChoiceField(
        queryset=CostProjectUnified.objects.none(),
        required=True,
        label="选择项目",
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_selected_project'})
    )
    
    # 项目编号（只读显示）
    display_project_code = forms.CharField(
        required=False,
        label="项目编号",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;',
            'id': 'id_display_project_code'
        })
    )
    
    # 项目名称（只读显示）
    display_project_name = forms.CharField(
        required=False,
        label="项目名称",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;',
            'id': 'id_display_project_name'
        })
    )
    
    class Meta:
        model = CostProjectUnified
        fields = [
            'selected_project', 'display_project_code', 'display_project_name',
            'plan_compiler', 'plan_compiler_personnel', 'plan_compilation_amount',
            'plan_first_reviewer', 'plan_first_reviewer_personnel', 'plan_first_reviewer_department',
            'plan_first_review_start_time', 'plan_first_review_planned_duration', 'plan_first_review_planned_completion',
            'plan_second_reviewer', 'plan_second_reviewer_personnel', 'plan_second_reviewer_department',
            'plan_second_review_start_time', 'plan_second_review_planned_duration', 'plan_second_review_planned_completion',
            'plan_third_reviewer', 'plan_third_reviewer_personnel', 'plan_third_reviewer_department',
            'plan_third_review_start_time', 'plan_third_review_planned_duration', 'plan_third_review_planned_completion',
        ]
        widgets = {
            'plan_compiler': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_compiler_personnel': forms.Select(attrs={'class': 'form-select'}),
            'plan_compilation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'plan_first_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_first_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'plan_first_reviewer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_first_review_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plan_first_review_planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'plan_first_review_planned_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plan_second_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_second_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'plan_second_reviewer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_second_review_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plan_second_review_planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'plan_second_review_planned_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plan_third_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_third_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'plan_third_reviewer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_third_review_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plan_third_review_planned_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'plan_third_review_planned_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = [
                'plan_compiler_personnel',
                'plan_first_reviewer_personnel',
                'plan_second_reviewer_personnel',
                'plan_third_reviewer_personnel',
            ]
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 动态设置项目选择器的 queryset
        if tenant:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
        else:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
        
        # 编辑模式隐藏项目选择器并设置初始值
        if self.instance.pk:
            self.fields['selected_project'].initial = self.instance.id
            self.fields['selected_project'].widget = forms.HiddenInput()
            self.fields['selected_project'].required = False
            # 编辑模式下填充项目编号和名称
            if self.instance.project_code:
                self.fields['display_project_code'].initial = self.instance.project_code
            if self.instance.project_name:
                self.fields['display_project_name'].initial = self.instance.project_name


class CostTaskImplementationForm(forms.ModelForm):
    """造价咨询任务实施表单 - 统一表模型"""
    
    # 项目选择字段
    selected_project = forms.ModelChoiceField(
        queryset=CostProjectUnified.objects.none(),
        required=True,
        label="选择项目",
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_selected_project'})
    )
    
    # 项目编号（只读显示）
    display_project_code = forms.CharField(
        required=False,
        label="项目编号",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;',
            'id': 'id_display_project_code'
        })
    )
    
    # 项目名称（只读显示）
    display_project_name = forms.CharField(
        required=False,
        label="项目名称",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;',
            'id': 'id_display_project_name'
        })
    )
    
    class Meta:
        model = CostProjectUnified
        fields = [
            'selected_project', 'display_project_code', 'display_project_name',
            'impl_compiler', 'impl_compiler_personnel', 'impl_compilation_amount',
            'impl_compilation_start', 'impl_compilation_end', 'impl_compilation_actual_duration',
            'impl_first_reviewer', 'impl_first_reviewer_personnel',
            'impl_first_review_start', 'impl_first_review_end', 'impl_first_review_actual_duration',
            'impl_first_review_progress_result',
            'impl_second_reviewer', 'impl_second_reviewer_personnel',
            'impl_second_review_start', 'impl_second_review_end', 'impl_second_review_actual_duration',
            'impl_second_review_progress_result',
            'impl_third_reviewer', 'impl_third_reviewer_personnel',
            'impl_third_review_start', 'impl_third_review_end', 'impl_third_review_actual_duration',
            'impl_third_review_progress_result',
            'implementation_status',
        ]
        widgets = {
            'impl_compiler': forms.TextInput(attrs={'class': 'form-control'}),
            'impl_compiler_personnel': forms.Select(attrs={'class': 'form-select'}),
            'impl_compilation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'impl_compilation_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_compilation_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_compilation_actual_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'impl_first_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'impl_first_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'impl_first_review_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_first_review_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_first_review_actual_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'impl_first_review_progress_result': forms.TextInput(attrs={'class': 'form-control'}),
            'impl_second_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'impl_second_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'impl_second_review_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_second_review_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_second_review_actual_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'impl_second_review_progress_result': forms.TextInput(attrs={'class': 'form-control'}),
            'impl_third_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'impl_third_reviewer_personnel': forms.Select(attrs={'class': 'form-select'}),
            'impl_third_review_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_third_review_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'impl_third_review_actual_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'impl_third_review_progress_result': forms.TextInput(attrs={'class': 'form-control'}),
            'implementation_status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 动态设置项目选择器的 queryset
        if tenant:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
        else:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
        
        # 编辑模式隐藏项目选择器并设置初始值
        if self.instance.pk:
            # 编辑时，实例本身就是项目记录，设置为自身
            self.fields['selected_project'].initial = self.instance.id
            self.fields['selected_project'].widget = forms.HiddenInput()
            self.fields['selected_project'].required = False
            # 编辑模式下填充项目编号和名称
            if self.instance.project_code:
                self.fields['display_project_code'].initial = self.instance.project_code
            if self.instance.project_name:
                self.fields['display_project_name'].initial = self.instance.project_name
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = [
                'impl_compiler_personnel',
                'impl_first_reviewer_personnel',
                'impl_second_reviewer_personnel',
                'impl_third_reviewer_personnel',
            ]
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)


class CostReviewResultForm(forms.ModelForm):
    """造价咨询审核成果表单 - 统一表模型"""
    
    # 项目选择字段
    selected_project = forms.ModelChoiceField(
        queryset=CostProjectUnified.objects.none(),
        required=True,
        label="选择项目",
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_selected_project'})
    )
    
    # 项目编号（只读显示）
    display_project_code = forms.CharField(
        required=False,
        label="项目编号",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;',
            'id': 'id_display_project_code'
        })
    )
    
    # 项目名称（只读显示）
    display_project_name = forms.CharField(
        required=False,
        label="项目名称",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;',
            'id': 'id_display_project_name'
        })
    )
    
    class Meta:
        model = CostProjectUnified
        fields = [
            'selected_project', 'display_project_code', 'display_project_name',
            'review_compiler', 'review_compilation_amount',
            'review_first_submission', 'review_first_result', 'review_first_reduction',
            'review_first_reduction_rate', 'review_first_review_evaluation',
            'review_second_submission', 'review_second_result', 'review_second_reduction',
            'review_second_reduction_rate', 'review_second_reviewer', 'review_second_evaluation',
            'review_third_submission', 'review_third_result', 'review_third_reduction',
            'review_third_reduction_rate', 'review_third_reviewer', 'review_third_evaluation',
            'review_final_approved_amount',
        ]
        widgets = {
            'review_compiler': forms.TextInput(attrs={'class': 'form-control'}),
            'review_compilation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_first_submission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_first_result': forms.TextInput(attrs={'class': 'form-control'}),
            'review_first_reduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_first_reduction_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_first_review_evaluation': forms.TextInput(attrs={'class': 'form-control'}),
            'review_second_submission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_second_result': forms.TextInput(attrs={'class': 'form-control'}),
            'review_second_reduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_second_reduction_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_second_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'review_second_evaluation': forms.TextInput(attrs={'class': 'form-control'}),
            'review_third_submission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_third_result': forms.TextInput(attrs={'class': 'form-control'}),
            'review_third_reduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_third_reduction_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'review_third_reviewer': forms.TextInput(attrs={'class': 'form-control'}),
            'review_third_evaluation': forms.TextInput(attrs={'class': 'form-control'}),
            'review_final_approved_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['impl_compiler_personnel', 'impl_first_reviewer_personnel', 'impl_second_reviewer_personnel', 'impl_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['plan_compiler_personnel', 'plan_first_reviewer_personnel', 'plan_second_reviewer_personnel', 'plan_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 动态设置项目选择器的 queryset
        if tenant:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
        else:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
        
        # 编辑模式隐藏项目选择器并设置初始值
        if self.instance.pk:
            # 编辑时，实例本身就是项目记录，设置为自身
            self.fields['selected_project'].initial = self.instance.id
            self.fields['selected_project'].widget = forms.HiddenInput()
            self.fields['selected_project'].required = False


class CostPaymentStatusForm(forms.ModelForm):
    """造价咨询收费情况表单 - 统一表模型"""
    
    # 项目选择字段
    selected_project = forms.ModelChoiceField(
        queryset=CostProjectUnified.objects.none(),
        required=True,
        label="选择项目",
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CostProjectUnified
        fields = [
            'selected_project',
            'payment_invoice_amount', 'payment_is_invoiced',
            'payment_owner_payable', 'payment_owner_paid', 'payment_owner_pending',
            'payment_contractor_payable', 'payment_contractor_paid', 'payment_contractor_pending',
            'payment_is_settled',
        ]
        widgets = {
            'payment_invoice_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_is_invoiced': forms.Select(attrs={'class': 'form-select'}),
            'payment_owner_payable': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_owner_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_owner_pending': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_contractor_payable': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_contractor_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_contractor_pending': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_is_settled': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['impl_compiler_personnel', 'impl_first_reviewer_personnel', 'impl_second_reviewer_personnel', 'impl_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['plan_compiler_personnel', 'plan_first_reviewer_personnel', 'plan_second_reviewer_personnel', 'plan_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 动态设置项目选择器的 queryset
        if tenant:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
        else:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
        
        # 编辑模式隐藏项目选择器并设置初始值
        if self.instance.pk:
            # 编辑时，实例本身就是项目记录，设置为自身
            self.fields['selected_project'].initial = self.instance.id
            self.fields['selected_project'].widget = forms.HiddenInput()
            self.fields['selected_project'].required = False


class CostProjectArchiveForm(forms.ModelForm):
    """造价咨询项目存档表单 - 统一表模型"""
    
    # 项目选择字段
    selected_project = forms.ModelChoiceField(
        queryset=CostProjectUnified.objects.none(),
        required=True,
        label="选择项目",
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CostProjectUnified
        fields = [
            'selected_project',
            'archive_status', 'archive_electronic', 'archive_paper', 'archive_complete',
            'archive_location', 'archive_date', 'archive_remark',
            'archive_service_contract', 'archive_service_contract_type',
            'archive_submission_material', 'archive_submission_material_type',
            'archive_process_material', 'archive_process_material_type',
            'archive_inspection_record', 'archive_inspection_record_type',
            'archive_audit_report', 'archive_audit_report_type',
            'archive_other_document', 'archive_other_document_type',
        ]
        widgets = {
            'archive_status': forms.Select(attrs={'class': 'form-select'}),
            'archive_electronic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'archive_paper': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'archive_complete': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'archive_location': forms.TextInput(attrs={'class': 'form-control'}),
            'archive_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'archive_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archive_service_contract': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archive_service_contract_type': forms.TextInput(attrs={'class': 'form-control'}),
            'archive_submission_material': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archive_submission_material_type': forms.TextInput(attrs={'class': 'form-control'}),
            'archive_process_material': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archive_process_material_type': forms.TextInput(attrs={'class': 'form-control'}),
            'archive_inspection_record': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archive_inspection_record_type': forms.TextInput(attrs={'class': 'form-control'}),
            'archive_audit_report': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archive_audit_report_type': forms.TextInput(attrs={'class': 'form-control'}),
            'archive_other_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archive_other_document_type': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['impl_compiler_personnel', 'impl_first_reviewer_personnel', 'impl_second_reviewer_personnel', 'impl_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['plan_compiler_personnel', 'plan_first_reviewer_personnel', 'plan_second_reviewer_personnel', 'plan_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 动态设置项目选择器的 queryset
        if tenant:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
        else:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
        
        # 编辑模式隐藏项目选择器并设置初始值
        if self.instance.pk:
            # 编辑时，实例本身就是项目记录，设置为自身
            self.fields['selected_project'].initial = self.instance.id
            self.fields['selected_project'].widget = forms.HiddenInput()
            self.fields['selected_project'].required = False
            # 关键修复：在编辑模式下，将 queryset 设置为包含当前实例，避免验证错误
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(pk=self.instance.pk)
        
        # 编辑模式下，archive_status 字段由工作流自动更新，不需要在表单中提交
        if self.instance.pk:
            self.fields['archive_status'].required = False
            self.fields['archive_status'].widget = forms.HiddenInput()


class CostRemunerationDistributionForm(forms.ModelForm):
    """造价咨询酬劳分配表单 - 统一表模型"""
    
    # 项目选择字段
    selected_project = forms.ModelChoiceField(
        queryset=CostProjectUnified.objects.none(),
        required=True,
        label="选择项目",
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CostProjectUnified
        fields = [
            'selected_project',
            'remuneration_calculation_type', 'remuneration_calculation_base',
            'remuneration_total_cost', 'remuneration_reduced_amount', 'remuneration_total_remuneration',
            'remuneration_calculation_formula', 'remuneration_distribution_status',
            'remuneration_compiler_ratio', 'remuneration_first_reviewer_ratio',
            'remuneration_second_reviewer_ratio', 'remuneration_third_reviewer_ratio',
        ]
        widgets = {
            'remuneration_calculation_type': forms.Select(attrs={'class': 'form-select'}),
            'remuneration_calculation_base': forms.Select(attrs={'class': 'form-select'}),
            'remuneration_total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remuneration_reduced_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remuneration_total_remuneration': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remuneration_calculation_formula': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remuneration_distribution_status': forms.Select(attrs={'class': 'form-select'}),
            'remuneration_compiler_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remuneration_first_reviewer_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remuneration_second_reviewer_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remuneration_third_reviewer_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['impl_compiler_personnel', 'impl_first_reviewer_personnel', 'impl_second_reviewer_personnel', 'impl_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = ['plan_compiler_personnel', 'plan_first_reviewer_personnel', 'plan_second_reviewer_personnel', 'plan_third_reviewer_personnel']
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)
        
        # 动态设置项目选择器的 queryset
        if tenant:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
        else:
            self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
        
        # 编辑模式隐藏项目选择器并设置初始值
        if self.instance.pk:
            # 编辑时，实例本身就是项目记录，设置为自身
            self.fields['selected_project'].initial = self.instance.id
            self.fields['selected_project'].widget = forms.HiddenInput()
            self.fields['selected_project'].required = False


class CostRemunerationItemForm(forms.ModelForm):
    """造价咨询酬劳分配明细表单"""
    
    class Meta:
        model = CostRemunerationItem
        fields = '__all__'
        widgets = {
            'distribution': forms.Select(attrs={'class': 'form-select'}),
            # Personnel和Department外键字段
            'personnel': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            # 原有字段
            'person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'distribution_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'calculated_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 为人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant and 'personnel' in self.fields:
            self.fields['personnel'].queryset = Personnel.objects.filter(tenant=tenant)
