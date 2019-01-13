from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect

from .models import Race
from .models import League
from .models import Team
from .models import Rider
from .models import Participation

from .forms import CreateLeagueForm
from .forms import CreateTeamForm
from .forms import SignUpForm

def home(request):
    # latest_races_list = Race.objects.order_by("-starts")
    latest_races_list = Race.objects.filter(is_classic=1).order_by('starts')
    context = {'latest_races_list': latest_races_list}
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
    # race = get_object_or_404(Race,slug=slug)
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

def team_add(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/thanks/')
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            t = Team(
                name = name,
                user = request.user
            )
            t.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = CreateTeamForm()
    return render(request, 'teams/add.html', {'form': form}) 

def rider_show(request,id):
    rider = get_object_or_404(Rider,id=id)
    return render(request, 'riders/detail.html',{'rider': rider})

def league_add(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/thanks/')        
    if request.method == 'POST':
        form = CreateLeagueForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            is_private = form.cleaned_data['is_private']
            password = form.cleaned_data['password']
            l = League(
                name = name,
                owner = request.user
            )
            l.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = CreateLeagueForm()
    return render(request, 'leagues/add.html', {'form': form}) 