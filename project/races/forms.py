from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import League
from .models import Team
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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

class TeamJoinLeagueForm(forms.Form):

    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        password = self.cleaned_data['password']
        
        if password == 'password':
            raise forms.ValidationError(_("'password' is a terrible password"))
        return data