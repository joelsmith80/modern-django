from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import League
from .models import Team
from .models import Roster
from .models import Race
from .models import Participation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password

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

class CreateRosterForm(ModelForm):

    team_id = forms.CharField(widget=forms.HiddenInput())
    # picks = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,required=False,choices=[])
    picks = "Luna"

    class Meta:
        model = Roster
        fields = ['team_id']

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id',None)
        self.race_id = kwargs.pop('race_id',None)
        self.team_id = kwargs.pop('team_id',None)
        self.picks = kwargs.pop('picks',None)
        self.riders_per_roster = kwargs.pop('riders_per_roster',None)
        super(CreateRosterForm,self).__init__(*args,**kwargs)

    def clean(self):
        
        # bail if we don't have a race
        try:
            race = Race.objects.get(pk=self.race_id)
        except Exception as e:
            raise forms.ValidationError(_("Somehow this race has ceased to exist..."))

        # bail if this team doesn't exist
        try:
            team = Team.objects.get(pk=self.team_id)
        except Exception as e:
            raise forms.ValidationError(_("Somehow this team has ceased to exist..."))

        # bail if this isn't user's team
        if team.user_id is not self.user_id:
            raise forms.ValidationError(_("Nice try, bub, but this ain't your team."))

        # bail if it's too late to draft this race
        if race.is_locked:
            raise forms.ValidationError(_("Sorry, but it's too late to draft for this race."))

        # cast any picks to integers; bail if none
        self.picks = [int(numeric_string) for numeric_string in self.picks] if self.picks else False
        if not self.picks:
            raise forms.ValidationError(_("You don't pick anybody. What's the point of that?"))

        # check that all picks are valid participants; bail if not
        for participant_id in self.picks:
            try:
                participant = Participation.objects.get(pk=participant_id,race_id=self.race_id)
            except Exception as e:
                raise forms.ValidationError(_("Hmm, you picked a guy that isn't in this race..."))

        # bail if we have too many picks
        if len(self.picks) > self.riders_per_roster:
            raise forms.ValidationError(_("Easy, there. You picked too many riders."))
        
        # bail if we don't have enough picks
        if len(self.picks) < self.riders_per_roster:
            raise forms.ValidationError(_("You didn't pick enough riders. Fill 'er up."))

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
                if(check_password(password,l.password)):
                    self.cleaned_data['password'] = True
                else:
                    raise forms.ValidationError(_("That's not the right league password, bub."))
                    
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
            