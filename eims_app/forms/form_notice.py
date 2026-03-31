from django import forms
from eims_app.models import Notice

class NoticeForm(forms.ModelForm):
    """通知公告表单（优化版 - 必填标题和关键字）"""
    class Meta:
        model = Notice
        fields = '__all__'
        exclude = ['read_count', 'update_time', 'is_deleted', 'file_name', 'file_size', 'file_type', 'create_time']
        widgets = {
            'notice_code': forms.TextInput(attrs={'class': 'form-control'}),
            'notice_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入通知标题', 'required': True}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入关键字，用逗号或空格分隔'}),
            'notice_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '请选择'), ('通知', '通知'), ('公告', '公告'), ('预警', '预警'), ('提醒', '提醒')
            ]),
            'notice_scope': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：全员/工程部/张三，李四'}),
            'notice_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attach_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.zip,.rar'}),
            'publish_person': forms.TextInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'invalid_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notice_status': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '请选择'), ('草稿', '草稿'), ('已发布', '已发布'), ('已撤回', '已撤回'), ('已过期', '已过期')
            ]),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
