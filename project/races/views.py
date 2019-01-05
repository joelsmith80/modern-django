from django.shortcuts import get_object_or_404, render

from .models import Race
from .models import League
from .models import Team
from .models import Rider

def home(request):
    # latest_races_list = Race.objects.order_by("-starts")
    latest_races_list = Race.objects.filter(is_classic=1).order_by('starts')
    context = {'latest_races_list': latest_races_list}
    return render(request, 'races/index.html', context)

def race_show(request,slug):
    # race = get_object_or_404(Race,slug=slug)
    race = Race.objects.filter(slug=slug).order_by('-id')[0]
    return render(request, 'races/detail.html',{'race': race})

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
    return render(request, 'teams/detail.html',{'team': team})

def rider_show(request,id):
    rider = get_object_or_404(Rider,id=id)
    return render(request, 'riders/detail.html',{'rider': rider})