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

class TeamJoinLeagueForm(ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(),required=False)
    league_id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = League
        fields = ['password','league_id']

    def __init__(self, *args,**kwargs):
        self.team = kwargs.pop('team',None)
        self.user_id = kwargs.pop('user_id',None)
        super(TeamJoinLeagueForm,self).__init__(*args,**kwargs)

    def clean(self):
        
        league_id = self.cleaned_data['league_id']
        
        # get the league object
        try:
            l = League.objects.get(pk=league_id)
        except League.DoesNotExist:
            raise forms.ValidationError(_("Not sure how you managed this, but that league doesn't actually exist."))

        # kick out for password violations
        if l.is_private:
            if 'password' not in self.cleaned_data:
                    raise forms.ValidationError(_("Private leagues require a password."))
            else:
                password = self.cleaned_data['password']
                if password != l.password:
                    raise forms.ValidationError(_("That's not the right league password, bub."))
                else:
                    self.cleaned_data['password'] = True

        # fail if league is full
        if l.is_full:
            raise forms.ValidationError(_("Sorry, but that league is full."))

        # fail is team already in league
        if l.has_team(self.team.id):
            raise forms.ValidationError(_("Oddly, your team is already in this league..."))

        # fail if user is already in league
        if l.has_user(self.user_id):
            raise forms.ValidationError(_("You already have another team in this league."))

        # fail if team is already in some league
        if self.team.league is not None:
            raise forms.ValidationError(_("Sorry, but this team is already in another league."))
            