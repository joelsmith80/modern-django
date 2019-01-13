from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import League
from .models import Team

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class CreateLeagueForm(ModelForm):
    class Meta:
        model = League
        fields = ['name','is_private','password']

class CreateTeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name']
