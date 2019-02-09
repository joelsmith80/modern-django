import logging

from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import Race
from .models import League
from .models import Team
from .models import Rider
from .models import Participation
from .models import SiteOption
from .models import Roster
from .models import FinalResult

from .forms import CreateLeagueForm
from .forms import CreateTeamForm
from .forms import SignUpForm
from .forms import TeamJoinLeagueForm
from .forms import CreateRosterForm

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
    rows = False
    race = Race.objects.filter(slug=slug).order_by('-id')[0]
    results = race.has_results()
    if results:
        rows = {
            'overall_results': results
        }
    else:
        participants = Participation.objects.filter(race=race.id).order_by('bib')
        formatted = Participation.format_for_table_rows(participants)
        rows = {
            'overall_results': formatted
        }
    context = {
        'race': race,
        'rows': rows
    }
    return render(request, 'races/detail.html', context)

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
    teams_per_league = SiteOption.objects.only('opt_value').get(opt_key='classics_teams_per_league')
    teams_per_league = int(teams_per_league.opt_value)
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
            l.refresh_from_db()
            num_teams = l.team_set.count()
            if num_teams >= teams_per_league:
                l.is_full = True
                l.save()
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
    if(team_belongs_to_user):
        for r in races:
            if(team.has_roster_for_race(r.id)):
                r.has_roster = True
    context = {
        'team': team,
        'races': races,
        'team_belongs_to_user': team_belongs_to_user
    }
    return render(request, 'teams/detail.html',context)

def team_race(request,id,slug):
    
    team = get_object_or_404(Team,id=id)
    race = Race.objects.filter(slug=slug).order_by('-id')[0]
    results = race.has_results()
    race.has_results = True if results else False
    team_belongs_to_user = True if request.user.id == team.user_id else False
    rows = {}
    messages = {}
    context = {}

    if results:
        team_results = team.has_results_for_race( race )
        if team_results:
            rows['team_results'] = team_results.get('rows')
            if 'roster_total' in team_results:
                context['roster_total'] = team_results['roster_total']
        else:
            messages['no_team_results'] = "Sorry, but this team doesn't have any results for this race."
        rows['overall_results'] = results
        messages['table_hed'] = "Race Results"
        messages['draft_button'] = None

    # else if no results
    else:
        
        team_results = None
        messages['no_overall_results'] = "Sorry, but there aren't any overall results for this race."
        

        if team_belongs_to_user:
            
            # look for a roster for this race
            roster = team.has_roster_for_race(race.id)
            
            # if we found a roster for this race
            if roster:
                messages['table_hed'] = "Your Riders For This Race"
                context['roster'] = roster
                picks = roster.picks.order_by('-val').all()
                rows = picks
            
            # else if we didn't find a roster for this race
            else:

                messages['table_hed'] = "Draft a Team For This Race"

                # get any available riders for this race
                picks = Participation.objects.filter(race=race.id).order_by('-val')

                # if picks are ready
                if picks:
                    context['picks'] = picks
                    context['redirect_on_success'] = "draft"
                    rows = picks
                
                # else if picks aren't ready yet
                else:
                    messages['no_participants'] = "Sorry, but there aren't any riders signed up for this race yet. As soon as they sign in, you'll be able to stock your roster."
        
        # else if this is not the team owner
        else:
            messages['no_results_for_this_team'] = "This team doesn't have any results for this race yet."
            

    # before the race, when there ARE rosters: show the riders, and show draft button if not drafted
    # before the race, if drafted: show the draft picks (if race not locked, show draft button still)
    # once there are results: show the results

    context['team'] = team
    context['race'] = race
    context['team_belongs_to_user'] = team_belongs_to_user  
    context['rows'] = rows
    context['messages'] = messages
    return render(request, 'teams/race.html',context)

@login_required
def team_race_draft(request,id,slug):

    # stuff we're going to need regardless
    team = get_object_or_404(Team,id=id)
    race = Race.objects.filter(slug=slug).order_by('-id')[0]
    riders = Participation.objects.filter(race=race.id).order_by('-val')
    team_belongs_to_user = True if request.user.id == team.user_id else False
    try:
        roster = Roster.objects.order_by('-val').get(race = race, team = team)
    except ObjectDoesNotExist:
        roster = None
    option = SiteOption()
    riders_per_roster = option.get_option('classics_riders_per_roster')
    context = {
        'team': team,
        'race': race,
        'riders': riders,
        'team_belongs_to_user': team_belongs_to_user,
        'roster': roster
    }

    # handle form submissions
    if request.method == 'POST':

        # bail if not this user's team (we also do this on the form template itself)
        if not team_belongs_to_user:
            return HttpResponseRedirect(reverse('races:team_show',args=(team.id,)))
        
        # get the picks and validate the form
        picks = request.POST.getlist('picks',False)
        form = CreateRosterForm(
            request.POST, 
            user_id = request.user.id, 
            race_id = race.id, 
            team_id = team.id, 
            picks = picks,
            riders_per_roster = riders_per_roster
        )

        # do the deed, if we have everything we need
        if form.is_valid():
            
            picks = form.picks
            
            # handle a pre-existing roster
            if roster:
                r = roster;
                r.picks.clear()
                r.save()
            
            # handle a new roster
            else:
                r = Roster(
                    race = race,
                    team = team
                )
                r.save()
            
            # drop and re-add all the picks
            for p in picks:
                participant = Participation.objects.get(pk=p)
                r.picks.add(participant)
                r.save()

            print(request.POST)
            if 'redirect' in request.POST and request.POST['redirect'] == 'team':
                return HttpResponseRedirect(reverse('races:team_race',args=(team.id,race.slug)))
            
            roster = r
            context['rows'] = roster
    
    # otherwise set up the form for display
    else:
        form = CreateRosterForm()

    # in either case, merge available and picked riders to get ordered list for display in form
    if roster:
        ordered = []
        picks = roster.picks.order_by('-val').all()
        for p in picks:
            p.picked = True
            ordered.append(p)
        for r in riders:
            if r not in picks:
                ordered.append(r)
        context['riders'] = ordered
        context['rows'] = ordered
    
    context['form'] = form
    context['redirect_on_success'] = "draft";
    return render(request, 'teams/draft.html', context)

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