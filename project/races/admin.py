import environ 
import os
from django.conf import settings
from django.contrib import admin
from .models import Race, Rider, Participation, Team, League, Post, Roster, SiteOption, FinalResult
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
import random

class ParticipationInline(admin.TabularInline):
    model = Participation
    fields = ['rider','bib','squad','val']
    extra = 1

def record_race_results( modeladmin, request, queryset ):
    
    for obj in queryset:
        path = settings.APPS_DIR
        file = "races/data/" + obj.slug + ".csv"
        
        # try to open the file
        try: 
            f = open( os.path.join( settings.APPS_DIR, file ) )
        except FileNotFoundError:
            modeladmin.message_user(request, "Couldn't open the file for " + obj.name)
            continue
        
        # add/update the actual race results
        results = FinalResult.add_update_from_file(f,obj)

        # bail if that didn't work
        if not results:
            modeladmin.message_user(request, "There was a problem creating results for " + obj.name)
            continue

        # try to add/update the riders' fantasy scores
        Participation.add_update_scores( results )

        Participation.mark_dnf( results, obj )

        # try to add/update teams' roster points, depending on the riders' fantasy scores
        eligible_rosters = obj.get_active_rosters()
        if not eligible_rosters:
            modeladmin.message_user(request, "There were no rosters to update for " + obj.name)
            continue

        for r in eligible_rosters:
            try:
                picks = r.picks.all()
            except:
                picks = None
            if picks:
                roster_total_pts = picks.aggregate(Sum('classics_points'))
                r.pts = roster_total_pts['classics_points__sum']
                r.save()

def autodraft_for_race( modeladmin, request, queryset ):
    for obj in queryset:
        option = SiteOption()
        riders_per_roster = option.get_option('classics_riders_per_roster')
        teams_per_league = option.get_option('classics_teams_per_league')
        leagues_in_play = League.objects.filter(is_full=True, is_classic=True)
        riders = obj.participation_set.all()
        num_riders = len(riders)
        if not leagues_in_play: return None
        for l in leagues_in_play:
            eligible_teams = l.get_undrafted_teams_for_race( obj.id, riders_per_roster )
            if eligible_teams:
                for t in eligible_teams:
                    roster = t.has_roster_for_race( obj.id )
                    if not roster:
                        roster = Roster()
                        roster.race = obj
                        roster.team = t
                        roster.save()
                    randos = []
                    for x in range(int(riders_per_roster)):
                        randos.append(random.randint(0,int(num_riders-1)))
                    for r in randos:
                        pick_id = riders[r].id
                        pick = Participation.objects.get(pk=pick_id)
                        roster.picks.add(pick)
                        roster.save()


class RaceAdmin(admin.ModelAdmin):
    list_display = ('id','name','slug','starts','is_live','is_locked')
    list_display_links = ('name',)
    inlines = (ParticipationInline,)
    actions = [record_race_results,autodraft_for_race]

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('bib','rider','race','squad','dnf','val','classics_points')
    list_display_links = ('rider',)
    list_filter = ('race','squad')
    search_fields = ('rider__last_name',)
    ordering = ['-id']

    def formfield_for_foreignkey(self,db_field,request,**kwargs):
        if db_field.name == 'race':
            kwargs['queryset'] = Race.objects.filter(is_classic=True).order_by('starts')
        if db_field.name == 'rider':
            kwargs['queryset'] = Rider.objects.order_by('last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class RosterInline(admin.TabularInline):
    model = Roster
    extra = 1

class TeamAdmin(admin.ModelAdmin):
    list_display = ('id','name','user','league')
    list_display_links = ('name',)
    inlines = (RosterInline,)
    ordering = ['-id']

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('id','name','owner','is_classic','is_private','is_full','get_teams_count')
    list_display_links = ('name',)
    ordering = ['id']

class RiderAdmin(admin.ModelAdmin):
    list_display = ('full_name','id','country')
    search_fields = ('last_name','first_name','id')

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','date','race')

class OptionAdmin(admin.ModelAdmin):
    list_display = ('id','opt_key','opt_value')
    list_display_links = ('opt_key',)
    ordering = ['opt_key']

class RosterAdmin(admin.ModelAdmin):
    list_display = ('id','team','race','pts')
    list_display_links = ('team',)
    ordering = ['race','team']
    def formfield_for_foreignkey(self,db_field,request,**kwargs):
        if db_field.name == 'race':
            kwargs['queryset'] = Race.objects.filter(is_classic=True).order_by('starts')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def get_object(self, request, object_id, from_field=None):
        self.obj = super(RosterAdmin, self).get_object(request, object_id)
        return self.obj
    def formfield_for_manytomany(self,db_field,request,**kwargs):
        if db_field.name == 'picks':
            if hasattr(self,'obj'):
                kwargs['queryset'] = Participation.objects.filter(race=self.obj.race)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

class FinalResultAdmin(admin.ModelAdmin):

    list_display = ('id','place','rider','race')
    list_display_links = ('place','rider')
    search_fields = ('rider',)
    ordering = ['-race','place']

admin.site.register(Race, RaceAdmin)
admin.site.register(Participation,ParticipationAdmin)
admin.site.register(Team,TeamAdmin)
admin.site.register(League,LeagueAdmin)
admin.site.register(Rider,RiderAdmin)
admin.site.register(Post,PostAdmin)
admin.site.register(Roster,RosterAdmin)
admin.site.register(SiteOption,OptionAdmin)
admin.site.register(FinalResult,FinalResultAdmin)