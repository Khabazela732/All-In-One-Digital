from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from authentication.models import HostEmployer

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-xl', "placeholder":"Enter Your Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-xl', "placeholder":"Enter Your Password"}))


