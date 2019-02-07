from django.conf import settings
from django import forms
from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models import Sum

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
        results = FinalResult.objects.filter(
            race=self,rider__participation__race=self
        )
        if results.count() == 0:
            return False
        else:
            return FinalResult.format_for_table_rows(results)

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
            datum['whatever'] = "You know?"
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
        roster = self.has_roster_for_race( race )
        if not roster: return None
        picks = roster.picks.all()
        if not picks: return None
        ids = []
        for p in picks: ids.append(p.rider.id)
        team_results = FinalResult.objects.filter(
            race = race,
            rider__participation__race = race,
            rider__in = ids
        )
        if not team_results: return None
        results = {}
        results['rows'] = FinalResult.format_for_table_rows(team_results)
        try: roster_total = team_results.aggregate(Sum('rider__participation__classics_points')).get('rider__participation__classics_points__sum')
        except: roster_total = None
        results['roster_total'] = roster_total
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