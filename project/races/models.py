from django.conf import settings
from django import forms
from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from .helpers import *

class Rider(models.Model):

    class Meta:
        db_table = "riders"

    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    country = models.CharField(max_length=5)
    birthday = models.DateField(blank=True,null=True)
    pro_cycling = models.URLField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return self.last_name.upper() + ", " + self.first_name
    full_name.short_description = "Name";

    def __str__(self):
        return self.last_name + ", " + self.first_name

class Race(models.Model):

    class Meta:
        db_table = "races"

    name = models.CharField(max_length=200)
    slug = models.SlugField()
    year = models.PositiveSmallIntegerField()
    starts = models.DateField()
    ends = models.DateField()
    description = models.TextField(blank=True, null=True)
    start_city = models.CharField(max_length=200, blank=True, null=True)
    end_city = models.CharField(max_length=200, blank=True, null=True)
    distance = models.CharField(max_length=200, blank=True, null=True)
    num_stages = models.PositiveSmallIntegerField(default=1)
    link = models.URLField(blank=True)
    teams_per_league = models.PositiveSmallIntegerField(blank=True,null=True)
    free_stages = models.PositiveSmallIntegerField(blank=True,null=True)
    team_budget = models.PositiveSmallIntegerField(blank=True,null=True)
    team_roster_size = models.PositiveSmallIntegerField(blank=True,null=True)
    is_live = models.BooleanField(default=0,verbose_name="Live?")
    is_locked = models.BooleanField(default=1,verbose_name="Locked?")
    is_classic = models.BooleanField(default=0,verbose_name="Classic?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    riders = models.ManyToManyField(Rider, through='Participation')

    def __str__(self):
        return self.name + " (" + str(self.year) + ")"

    def has_results(self):
        results = {}
        finishers = self.get_finishers()
        if not finishers: return False
        results['finishers'] = finishers
        non_finishers = self.get_dnf()
        if non_finishers:
            results['dnf'] = non_finishers
        return results

    def get_finishers(self):
        results = FinalResult.objects.filter(
            race=self,rider__participation__race=self
        )
        if results.count() == 0:
            return False
        else:
            return FinalResult.format_for_table_rows(results)

    def get_dnf( self ):
        results = Participation.objects.filter(race=self,dnf=1).order_by('bib')
        if results: return Participation.format_for_table_rows(results)
        else: return None

    def get_participants(self):
        return Participation.objects.filter( race=self ).order_by('bib') 

    def get_active_rosters(self):
        try:
            rosters = Roster.objects.filter( race = self, team__league__is_classic=True, team__league__is_full=True )
            return rosters
        except:
            return None

    

class Participation(models.Model):

    class Meta:
        db_table = "participations"

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    bib = models.PositiveSmallIntegerField(null=True,blank=True)
    squad = models.CharField(max_length=200)
    dnf = models.PositiveSmallIntegerField(null=True,blank=True)
    comments = models.TextField(null=True,blank=True)
    role = models.CharField(max_length=200,blank=True,null=True)
    jersey_hunt = models.CharField(max_length=200,blank=True,null=True)
    val = models.PositiveSmallIntegerField(null=True,blank=True)
    classics_points = models.PositiveSmallIntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rider.last_name.upper() + ", " + self.rider.first_name

    def format_for_table_rows(queryset):
        data = []
        for r in queryset:
            datum = {};
            datum['bib'] = r.bib
            datum['rider'] = r.rider
            datum['team'] = r.squad
            datum['country'] = r.rider.country
            datum['val'] = r.val
            data.append(datum)
        return data

    def add_update_scores( final_result_queryset ):
        results = final_result_queryset
        option = SiteOption()
        pts_max = option.get_option('points_multiplier_max_pts')
        pts_min = option.get_option('points_multiplier_min_pts')
        factor_max = option.get_option('points_multiplier_max_factor')
        num_finishers = len(results)
        for r in results:
            try:
                entry = Participation.objects.get( rider_id = r.rider_id, race_id = r.race_id )
            except Exception as e:
                print( e )
            score = Participation.calculate_score( num_finishers, r.place, entry.val, pts_max, pts_min, factor_max )
            entry.classics_points = score
            entry.save()

    def calculate_score( num_finishers, place, initial_value, pts_max, pts_min, factor_max ):
        multi = Participation.calculate_points_multiplier( initial_value, pts_max, pts_min, factor_max )
        place = int(place)
        finishing_pts = (num_finishers - place) + 1
        return finishing_pts * multi

    def calculate_points_multiplier( initial_value, pts_max, pts_min, factor_max ):
        return round( (((factor_max - 1) * ((pts_max - initial_value) / (pts_max - pts_min))) + 1), 2)        

    def mark_dnf( final_result_queryset, race_obj ):
        results = final_result_queryset
        ids_of_riders_who_finished = []
        for r in results:
            ids_of_riders_who_finished.append(r.rider_id)
        all_participants = Participation.objects.filter( race = race_obj )
        if all_participants:
            for p in all_participants:
                if p.rider_id not in ids_of_riders_who_finished:
                    p.dnf = 1
                else:
                    p.dnf = None
                p.save()
        

class League(models.Model):

    class Meta:
        db_table = "leagues"

    name = models.CharField(max_length=200)
    race = models.ForeignKey(Race, blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, on_delete=models.SET_DEFAULT)
    password = models.CharField(max_length=200, blank=True, null=True)
    has_drafted = models.BooleanField(default=0)
    is_classic = models.BooleanField(default=0)
    is_private = models.BooleanField(default=0)
    is_full = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        full = self.should_be_full()
        if full: self.is_full = True
        else: self.is_full = False
        super(League, self).save(*args, **kwargs)

    def access_type(self):
        return "Private" if self.is_private else "Public"

    def has_team(self,team_id):
        team_count = Team.objects.filter(id=team_id,league=self.id).count()
        return True if team_count > 0 else False

    def has_user(self,user_id):
        query = Team.objects.filter(league=self.id,user=user_id).count()
        return True if query > 0 else False

    def get_undrafted_teams_for_race( self, race_id, riders_per_roster ):
        teams = self.team_set.all()
        if not teams: return None
        results = []
        for t in teams:
            roster = t.has_roster_for_race( race_id )
            if roster:
                picks = roster.picks.all()
                if not picks:
                    results.append(t)
                elif len(picks) > riders_per_roster:
                    results.append(t)
            else:
                results.append(t)
        return results

    def should_be_full(self):
        teams_per_league = get_option('classics_teams_per_league')
        num_teams = self.get_teams_count()
        if num_teams == teams_per_league: return True
        else: return False

    def get_teams(self):
        teams = Team.objects.filter( league=self )
        if not teams: return None
        for t in teams:
            t.points = t.get_season_total()
        teams.order_by('-points','name')
        return self.get_place_order(teams)

    def get_races(self):
        races =  Race.objects.filter(is_classic=1).order_by('starts')
        for r in races:
            r.results = self.get_standings_for_race( r )
        return races

    def get_standings_for_race( self, race ):
        results = race.has_results()
        if not results: return None
        teams = Team.objects.filter( league=self )
        if not teams: return None
        for t in teams:
            t.points = t.get_race_total( race )
        return self.get_place_order(teams)

    def get_rosters_for_race( self, race ):
        return Roster.objects.filter( race=race, team__league=self )

    def get_teams_count(self):
        return len(self.team_set.all())
    get_teams_count.short_description = "Teams"

    def get_place_order( self, queryset ):
        i = 1
        hi_score = queryset[0].points
        for team in queryset:
            if team.points != hi_score:
                i = i + 1
            team.place = i
            hi_score = team.points
        return queryset


            

class Team(models.Model):

    class Meta:
        db_table = "teams"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, on_delete=models.SET_DEFAULT)
    name = models.CharField(max_length=200)
    league = models.ForeignKey(League, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def can_enter_league(self,league):
        if league.is_full:
            return False
        return True

    def get_races( self ):
        races = Race.objects.filter(is_classic=1).order_by('starts')
        if not races: return None
        for r in races:
            r.results = self.has_results_for_race( r )
        return races

    def has_roster_for_race(self,race_id):
        roster = self.get_roster_for_race( race_id )
        if roster: return roster
        else: return None

    def get_roster_for_race( self, race_id ):
        try: return Roster.objects.get( race_id=race_id, team=self )
        except: return None

    def has_results_for_race( self, race ):
        results = self.get_results_for_race( race )
        if results: return results
        else: return False

    def get_results_for_race( self, race ):

        # get roster; bail if it doesn't exist
        roster = self.has_roster_for_race( race )
        if not roster: return None

        # get the picks from the roster; bail if there aren't any
        picks = roster.picks.all()
        if not picks: return None

        # create a list of just the pick ids
        ids = []
        for p in picks: ids.append(p.rider.id)

        # search for FinalResults that match the pick ids; bail if none
        team_results = FinalResult.objects.filter(
            race = race,
            rider__participation__race = race,
            rider__in = ids
        )
        if not team_results: return None

        # stuff the return object with the results
        results = {}
        results['finishers'] = FinalResult.format_for_table_rows(team_results)

        # try to calculate the team's total score; add it to return object
        try: roster_total = team_results.aggregate(Sum('rider__participation__classics_points')).get('rider__participation__classics_points__sum')
        except: roster_total = None
        results['roster_total'] = roster_total

        # return non-finishers by comparing picks with list of finishers
        finisher_ids = []
        for f in team_results:
            finisher_ids.append(f.rider_id)
        dnf = []
        for p in picks:
            if p.rider.id not in finisher_ids:
                dnf.append(p)
        if dnf:
            dnf = Participation.format_for_table_rows(dnf)
            results['dnf'] = dnf;
        return results

    def get_season_total( self ):
        season_total = 0
        all_rosters = self.get_all_rosters()
        try:    
            season_total = all_rosters.aggregate(Sum('pts')).get('pts__sum')
            if not season_total: season_total = 0
        except: season_total = 0
        return int(season_total)

    def get_race_total( self, race ):
        race_total = 0
        roster = self.has_roster_for_race(race)
        if not roster: return 0
        return int(roster.pts)

    def get_all_rosters( self ):
        return Roster.objects.filter( team = self )

    def get_all_picks( self ):
        results = Participation.objects.filter( roster__team=self )
        return results

class FinalResult(models.Model):

    class Meta:
        db_table = "final_results"
        unique_together = ('race','place',)

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    place = models.PositiveSmallIntegerField(null=True,blank=True)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
        # return self.place

    def format_for_table_rows(queryset):
        results = queryset.values(
            'place',
            'rider__id',
            'rider__last_name',
            'rider__first_name',
            'rider__participation__val',
            'rider__participation__classics_points',
            'rider__participation__bib',
            'rider__participation__squad',
            'rider__country'
        ).order_by('place')
        data = []
        for r in results:
            datum = {};
            datum['place'] = r['place']
            datum['id'] = r['rider__id']
            datum['rider'] = r['rider__last_name'] + ', ' + r['rider__first_name']
            datum['val'] = r['rider__participation__val']
            datum['points'] = r['rider__participation__classics_points']
            datum['bib'] = r['rider__participation__bib']
            datum['team'] = r['rider__participation__squad']
            datum['country'] = r['rider__country']
            data.append(datum)
        return data

    def add_update_from_file( blob, race_obj ):
        results = []
        frs = FinalResult.objects.filter( race = race_obj).delete()
        for line in blob:
            arr = line.rstrip().split(',')
            place = arr[1]
            bib = arr[2]
            rider_id = race_obj.participation_set.values('rider_id').get( bib = bib )
            rider_id = int(rider_id['rider_id'])
            record = FinalResult(
                place = place,
                race_id = race_obj.id,
                rider_id = rider_id
            )
            record.save()
            results.append(record)
        return results
            

class Stage(models.Model):

    class Meta:
        db_table = "stages"

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    stage_num = models.PositiveSmallIntegerField(default=1, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    distance = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    stage_type = models.CharField(max_length=200, blank=True, null=True)
    depart_city = models.CharField(max_length=200, blank=True, null=True)
    depart_lat = models.CharField(max_length=200, blank=True, null=True)
    depart_long = models.CharField(max_length=200, blank=True, null=True)
    arrive_city = models.CharField(max_length=200, blank=True, null=True)
    arrive_lat = models.CharField(max_length=200, blank=True, null=True)
    arrive_long = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField()
    is_doubled = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Jersey(models.Model):

    class Meta:
        db_table = "jerseys"

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Post(models.Model):

    class Meta:
        db_table = "posts"

    TYPE_CHOICES = (
        ('general','General'),
        ('preview','Preview'),
        ('review','Review'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField()
    body = models.TextField(blank=True, null=True)
    date = models.DateField()
    post_type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='general')
    race = models.ForeignKey(Race, blank=True, null=True, on_delete=models.SET_NULL)
    stage = models.ForeignKey(Stage, blank=True, null=True, on_delete=models.SET_NULL)
    riders = models.ManyToManyField(Rider)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Roster(models.Model):

    class Meta:
        db_table = "rosters"
        unique_together = (('team','race'),)
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    picks = models.ManyToManyField(Participation, blank=True)
    pts = models.PositiveSmallIntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SiteOption(models.Model):

    class Meta:
        db_table = "site_options"

    opt_key = models.CharField(max_length=255,unique=True)
    opt_value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_option( self, key, type = int ):
        try:
            raw = SiteOption.objects.only('opt_value').get(opt_key=key)
            if type is int:
                return int(raw.opt_value)
            else:
                return "Some other thing"
        except:
            return None