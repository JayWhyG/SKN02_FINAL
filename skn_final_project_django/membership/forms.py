from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser
from .models import Resume

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['이력서_이름', '이력서_파일']

class FindIDForm(forms.Form):
    email = forms.EmailField(label='이메일', max_length=254)