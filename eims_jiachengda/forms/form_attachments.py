from django import forms
from eims_app.models import NoticeAttachment, FileManageVersion

class NoticeAttachmentForm(forms.ModelForm):
    """通知公告附件表单"""
    class Meta:
        model = NoticeAttachment
        fields = ['file', 'remark']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.zip,.rar,.txt,.md'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '备注说明（可选）'
            }),
        }


class NoticeBatchUploadForm(forms.Form):
    """通知公告批量上传表单"""
    remark = forms.CharField(
        label='统一备注',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': '对所有文件的统一备注（可选）'
        })
    )


class FileManageVersionForm(forms.ModelForm):
    """文件管理版本更新表单"""
    class Meta:
        model = FileManageVersion
        fields = ['file', 'change_log']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.zip,.rar,.txt,.md'
            }),
            'change_log': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请填写本次更新的变更内容（必填）'
            }),
        }


class FileManageBatchUploadForm(forms.Form):
    """文件管理批量上传表单"""
    file_category = forms.CharField(
        label='文件类别',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '例：合同、人员、项目等'
        })
    )
    remark = forms.CharField(
        label='统一备注',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': '对所有文件的统一备注（可选）'
        })
    )
