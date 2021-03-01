from django.forms import ModelForm
from django import forms
from .models import LPGRecord

class LPGForm(forms.ModelForm):
    class Meta:
        model = LPGRecord
        fields = '__all__'
        exclude = ['side']




# 添加一下登录窗口的输入验证
class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label='用户名',
        error_messages={
            'required': '用户名不能为空'
        }
    )
    password = forms.CharField(
        required=True,
        label='密码',
        error_messages={
            'required': '密码不能为空',
        })


