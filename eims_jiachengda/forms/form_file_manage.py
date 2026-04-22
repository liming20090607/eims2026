from django import forms
from eims_app.models import FileManage
import hashlib

class FileForm(forms.ModelForm):
    """文件管理表单（验证 + 文件上传）"""
    # 只读字段：文件格式
    file_format = forms.CharField(
        label='文件格式',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'file_format',
            'name': 'file_format',
            'readonly': 'readonly',
            'placeholder': '自动识别'
        })
    )
    
    class Meta:
        model = FileManage
        fields = '__all__'
        exclude = ['file_size', 'file_type', 'publish_time', 'update_time', 'uploader']
        widgets = {
            'file_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'file_name',
                'name': 'file_name',
                'required': True
            }),
            'file_category': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'file_category',
                'name': 'file_category',
                'placeholder': '例：合同、人员、项目等',
                'required': True  # 必填字段
            }),
            'file_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'file_number',
                'name': 'file_number',
                'placeholder': '例：2026-001'
            }),
            'content_summary': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'id': 'content_summary',
                'name': 'content_summary',
                'placeholder': '请输入文件内容摘要'
            }),
            'file_path': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'file_path',
                'name': 'file_path',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'id': 'remark',
                'name': 'remark',
                'placeholder': '请输入备注信息'
            }),
        }
    
    # 自定义验证：自动设置上传人（已在视图中处理，移除此方法）
    # def clean_uploader(self):
    #     request = self.context.get('request') if hasattr(self, 'context') else None
    #     if request and request.user.is_authenticated:
    #         return request.user.username
    #     return '系统'
    
    def clean_file_category(self):
        """验证文件类别必须填写"""
        file_category = self.cleaned_data.get('file_category')
        if not file_category or not file_category.strip():
            raise forms.ValidationError('文件类别不能为空，请输入文件类别！')
        return file_category.strip()
    
    def clean_file_path(self):
        file = self.cleaned_data.get('file_path')
        if file:
            # 计算文件大小（KB）
            self.cleaned_data['file_size'] = file.size
        return file
