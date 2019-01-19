import logging

from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Race
from .models import League
from .models import Team
from .models import Rider
from .models import Participation

from .forms import CreateLeagueForm
from .forms import CreateTeamForm
from .forms import SignUpForm
from .forms import TeamJoinLeagueForm

logger = logging.getLogger(__name__)

def home(request):
    race_list = Race.objects.filter(is_classic=1).order_by('starts')
    team_list = None
    if request.user.is_authenticated:
        team_list = Team.objects.filter(user = request.user)
    context = {
        'race_list': race_list,
        'team_list': team_list
    }
    return render(request, 'races/index.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            user = authenticate(username=username,password=raw_password,email=email)
            login(request,user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request,'users/signup.html',{'form': form})

def race_show(request,slug):
    race = Race.objects.filter(slug=slug).order_by('-id')[0]
    participants = Participation.objects.filter(race=race.id).order_by('bib')
    return render(request, 'races/detail.html',{'race': race, 'participants': participants})

def leagues_index(request):
    leagues_list = League.objects.filter(is_classic=1).order_by('name')
    context = {'leagues': leagues_list}
    return render(request, 'leagues/index.html', context)

def league_show(request,id):
    league = get_object_or_404(League,id=id)
    teams_this_league = Team.objects.filter(league=id).order_by('name')
    return render(request, 'leagues/detail.html',{'league': league, 'teams': teams_this_league})

@login_required
def team_join_league(request,id):

    # get basic variables
    team = get_object_or_404(Team,id=id)
    team_belongs_to_user = True if request.user.id == team.user_id else False
    joinable_leagues = League.objects.filter(is_classic=True,is_full=False)
    context = {
        'team': team,
        'joinable_leagues': joinable_leagues,
        'team_belongs_to_user': team_belongs_to_user
    }

    # handle POST form submission
    if request.method == 'POST':
        form = TeamJoinLeagueForm(request.POST,team=team,user_id=request.user.id)
        context['form'] = form
        if form.is_valid():
            print("Form is valid")
            league_id = form.cleaned_data['league_id']
            l = League.objects.get(pk=league_id)
            team.league = l
            team.save()
            return HttpResponseRedirect(reverse('races:team_show',args=(id,)))
        else:
            print("Form was NOT valid")

    # handle GET requests for form
    else:
        form = TeamJoinLeagueForm()
        context['form'] = form
        if team.league is not None:
            return HttpResponseRedirect(reverse('races:team_show',args=(id,)))

    # send it off    
    return render(request, 'teams/join_league.html',context)

def teams_index(request):
    teams_list = Team.objects.order_by('name')
    context = {'teams': teams_list}
    return render(request, 'teams/index.html', context)

def team_show(request,id):
    team = get_object_or_404(Team,id=id)
    races = Race.objects.filter(is_classic=1).order_by('starts')
    team_belongs_to_user = True if request.user.id == team.user_id else False
    context = {
        'team': team,
        'races': races,
        'team_belongs_to_user': team_belongs_to_user
    }
    return render(request, 'teams/detail.html',context)

def team_race(request,id,slug):
    team = get_object_or_404(Team,id=id)
    race = Race.objects.filter(slug=slug).order_by('-id')[0]
    riders = Participation.objects.filter(race=race.id).order_by('bib')
    context = {
        'team': team,
        'race': race,
        'riders': riders
    }
    return render(request, 'teams/race.html',context)

@login_required
def team_add(request):
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            t = Team(
                name = name,
                user = request.user
            )
            t.save()
            return HttpResponseRedirect(reverse('races:team_show',args=(t.id,)))
    else:
        form = CreateTeamForm()        
    return render(request, 'teams/add.html', {'form': form}) 

def rider_show(request,id):
    rider = get_object_or_404(Rider,id=id)
    return render(request, 'riders/detail.html',{'rider': rider})

@login_required
def league_add(request):
    if request.method == 'POST':
        form = CreateLeagueForm(request.POST,request=request)
        if form.is_valid():
            name = form.cleaned_data['name']
            is_private = form.cleaned_data['is_private']
            password = form.cleaned_data['password']
            l = League(
                name = name,
                owner = request.user,
                is_private = is_private,
                is_classic = 1
            )
            if is_private:
                l.password = password
            l.save()
            return HttpResponseRedirect(reverse('races:league_show',args=(l.id,)))
    else:
        form = CreateLeagueForm()
    return render(request, 'leagues/add.html', {'form': form}) 