from django import forms
from django.utils import timezone
from datetime import date, timedelta
from ..models import MonthlyReport
from ..models.model_project_detail import ProjectDetail  # 改用 ProjectDetail

class MonthlyReportForm(forms.ModelForm):
    """月度报告填报表单"""
    
    # 只读字段，用于显示
    project_code_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '项目编号'
        }),
        label='项目编号'
    )
    
    reporter_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '填报人'
        }),
        label='填报人'
    )
    
    report_time_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '填报时间'
        }),
        label='填报时间'
    )
    
    class Meta:
        model = MonthlyReport
        fields = [
            'project', 'report_month', 'project_progress', 'current_status',
            'last_month_cumulative_output', 'monthly_output_value', 'current_cumulative_output',
            'last_month_cumulative_payment', 'monthly_payment', 'current_cumulative_payment', 
            'payment_description',
            'personnel_changes', 'total_personnel',
            'current_payment_request', 'payment_progress', 'payment_issues',
            'next_month_plan_amount', 'next_month_plan_detail', 'next_month_assistance'
        ]
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '选择要填报的项目'
            }),
            'report_month': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'month',
                'placeholder': '选择年月',
                'step': '1'  # 按月递增
            }),
            'project_progress': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '详细描述项目当前进度情况'
            }),
            'current_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'last_month_cumulative_output': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'monthly_output_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'current_cumulative_output': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'last_month_cumulative_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'monthly_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'current_cumulative_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'payment_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '详细描述回款情况'
            }),
            'personnel_changes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '描述本月人员变动情况，如：新增 3 人/离职 1 人'
            }),
            'total_personnel': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'current_payment_request': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_progress': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：已提交申请/审批中/已到账'
            }),
            'payment_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '需要协调的问题和建议'
            }),
            'next_month_plan_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'next_month_plan_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '详细的请款计划和安排'
            }),
            'next_month_assistance': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '需要公司或领导协助的事项'
            }),
        }
        labels = {
            'project': '项目名称',
            'report_month': '报告月份',
            'project_progress': '项目进度说明',
            'current_status': '当前状态',
            'last_month_cumulative_output': '上月累计产值 (元)',
            'monthly_output_value': '本月完成产值 (元)',
            'current_cumulative_output': '本月累计产值 (元)',
            'last_month_cumulative_payment': '上月累计回款 (元)',
            'monthly_payment': '本月回款金额 (元)',
            'current_cumulative_payment': '本月累计回款 (元)',
            'payment_description': '回款情况说明',
            'personnel_changes': '本月人员变动',
            'total_personnel': '当前总人数',
            'current_payment_request': '本月正在请款金额 (元)',
            'payment_progress': '本月请款进度',
            'payment_issues': '问题及建议',
            'next_month_plan_amount': '下月请款金额 (元)',
            'next_month_plan_detail': '具体请款计划',
            'next_month_assistance': '需要的协助',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        initial_project = kwargs.pop('initial_project', None)  # 从 URL 参数获取的初始项目
        super().__init__(*args, **kwargs)
        
        # 只允许用户选择自己负责的项目
        if user and not user.is_superuser:
            self.fields['project'].queryset = ProjectDetail.objects.filter(
                project_manager=user.username
            )
        elif user and user.is_superuser:
            self.fields['project'].queryset = ProjectDetail.objects.all()
        
        # 如果有初始项目，设置默认值并禁用项目选择
        if initial_project:
            self.fields['project'].initial = initial_project.pk
            self.fields['project'].widget.attrs['readonly'] = True
            self.fields['project_code_display'].initial = initial_project.project_code
        
        # 设置只读字段的初始值
        if user:
            self.fields['reporter_display'].initial = user.username
            
            # 新创建时设置填报时间
            if not self.instance.pk:
                now = timezone.now()
                self.fields['report_time_display'].initial = now.strftime('%Y-%m-%d %H:%M')
                self.fields['report_month'].initial = now.strftime('%Y-%m')
                
                # 尝试获取上月数据
                from datetime import datetime, timedelta
                current_date = now.replace(day=1)  # 设为本月 1 号
                last_month = (current_date - timedelta(days=1)).replace(day=1)
                
                # 查询上月的报告
                try:
                    # 使用字符串格式的月份
                    last_month_str = f"{last_month.year}-{last_month.month:02d}"
                    last_month_report = MonthlyReport.objects.filter(
                        project=initial_project,
                        report_year=last_month.year,
                        report_month=last_month_str
                    ).first()
                    
                    if last_month_report:
                        # 填充上月累计值
                        self.fields['last_month_cumulative_output'].initial = last_month_report.current_cumulative_output or 0
                        self.fields['last_month_cumulative_payment'].initial = last_month_report.current_cumulative_payment or 0
                    else:
                        # 没有上月报告，设置为 0
                        self.fields['last_month_cumulative_output'].initial = 0
                        self.fields['last_month_cumulative_payment'].initial = 0
                except Exception as e:
                    # 出现任何错误都设置为 0
                    self.fields['last_month_cumulative_output'].initial = 0
                    self.fields['last_month_cumulative_payment'].initial = 0
            else:
                # 编辑时显示已有数据
                self.fields['report_time_display'].initial = self.instance.create_time.strftime('%Y-%m-%d %H:%M') if self.instance.create_time else ''
                
                # 现在 report_month 是字符串格式 "YYYY-MM"
                if self.instance.report_month and isinstance(self.instance.report_month, str):
                    self.fields['report_month'].initial = self.instance.report_month
                else:
                    # 如果是旧数据（整数），转换为字符串
                    year = self.instance.report_year
                    month = self.instance.report_month
                    self.fields['report_month'].initial = f"{year}-{month:02d}"
                
                # 填充已有数据，确保不为 None
                self.fields['last_month_cumulative_output'].initial = self.instance.last_month_cumulative_output or 0
                self.fields['last_month_cumulative_payment'].initial = self.instance.last_month_cumulative_payment or 0
    
    def clean_report_month(self):
        """验证月份格式"""
        report_month = self.cleaned_data.get('report_month')
        
        if report_month:
            try:
                # 确保是字符串类型
                report_month_str = str(report_month).strip()
                
                # 处理可能的日期对象
                if hasattr(report_month, 'strftime'):
                    # 如果是日期对象，转换为 YYYY-MM 格式
                    report_month_str = report_month.strftime('%Y-%m')
                
                # 验证格式
                if '-' not in report_month_str:
                    raise forms.ValidationError('月份格式错误，应为 YYYY-MM')
                
                year, month = map(int, report_month_str.split('-'))
                
                if not (1 <= month <= 12):
                    raise forms.ValidationError('月份必须在 1-12 之间')
                
                if year < 2000 or year > 2100:
                    raise forms.ValidationError('年份必须在 2000-2100 之间')
                    
            except (ValueError, AttributeError) as e:
                raise forms.ValidationError('月份格式错误，应为 YYYY-MM 格式')
        
        # 返回字符串格式
        return report_month
    
    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        report_month = cleaned_data.get('report_month')
        
        if project and report_month:
            try:
                # 确保是字符串类型
                report_month_str = str(report_month).strip()
                
                # 处理可能的日期对象
                if hasattr(report_month, 'strftime'):
                    report_month_str = report_month.strftime('%Y-%m')
                
                if '-' not in report_month_str:
                    return cleaned_data
                
                year, month = map(int, report_month_str.split('-'))
                
                # 检查是否重复填报（使用字符串比较）
                existing = MonthlyReport.objects.filter(
                    project=project,
                    report_year=year,
                    report_month=report_month_str  # 直接使用字符串
                )
                if existing.exists() and (not self.instance.pk or self.instance.pk != existing.first().pk):
                    raise forms.ValidationError(f'{project.project_name} 的 {report_month_str} 报告已存在！')
            except (ValueError, AttributeError):
                # 如果解析失败，跳过重复检查
                pass
        
        return cleaned_data


class MonthlyReportFilterForm(forms.Form):
    """月度报告筛选表单"""
    
    STATUS_CHOICES = [
        ('', '全部状态'),
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('overdue', '已逾期'),
    ]
    
    report_month = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'YYYY-MM',
            'pattern': r'\d{4}-\d{2}'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    project = forms.ModelChoiceField(
        queryset=ProjectDetail.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
