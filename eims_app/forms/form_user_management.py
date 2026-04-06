from django import forms
from django.contrib.auth import get_user_model
from eims_app.models import Employee

User = get_user_model()

class BatchUserCreateForm(forms.Form):
    """批量创建用户表单"""
    
    # 默认密码设置
    default_password = forms.CharField(
        max_length=50,
        initial='Abc123456!',
        required=True,
        label='默认密码',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入默认密码',
            'style': 'width: 300px;'
        }),
        help_text='所有新创建用户的初始密码'
    )
    
    # 选择员工
    select_all = forms.BooleanField(
        required=False,
        label='全选',
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'id': 'select-all-users',
            'class': 'form-check-input'
        })
    )

class PasswordResetForm(forms.Form):
    """密码重置表单"""
    
    user_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput()
    )
    
    new_password = forms.CharField(
        max_length=50,
        required=True,
        label='新密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入新密码',
            'style': 'width: 300px;'
        })
    )
    
    confirm_password = forms.CharField(
        max_length=50,
        required=True,
        label='确认密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请再次输入新密码',
            'style': 'width: 300px;'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('两次输入的密码不一致')
        
        return cleaned_data
