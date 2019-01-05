from django.conf import settings
from django import forms
from django.db import models

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
    is_live = models.BooleanField(default=0)
    is_locked = models.BooleanField(default=1)
    is_classic = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + " (" + str(self.year) + ")"

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

    def __str__(self):
        return self.last_name + ", " + self.first_name

class Participation(models.Model):

    class Meta:
        db_table = "participations"

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    bib = models.PositiveSmallIntegerField(null=True,blank=True)
    team = models.CharField(max_length=200)
    dnf = models.PositiveSmallIntegerField(null=True,blank=True)
    comments = models.TextField(null=True,blank=True)
    role = models.CharField(max_length=200,blank=True,null=True)
    jersey_hunt = models.CharField(max_length=200,blank=True,null=True)
    val = models.PositiveSmallIntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class League(models.Model):

    class Meta:
        db_table = "leagues"

    name = models.CharField(max_length=200)
    race = models.ForeignKey(Race, blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, on_delete=models.SET_DEFAULT)
    password = models.CharField(max_length=32, blank=True, null=True)
    has_drafted = models.BooleanField(default=0)
    is_classic = models.BooleanField(default=0)
    is_private = models.BooleanField(default=0)
    is_full = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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

class FinalResult(models.Model):

    class Meta:
        db_table = "final_results"

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    place = models.PositiveSmallIntegerField(null=True,blank=True)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.place

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