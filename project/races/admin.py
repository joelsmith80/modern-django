from django.contrib import admin

from .models import Race, Rider, Participation, Team, League, Post


class RaceAdmin(admin.ModelAdmin):
    list_display = ('name','starts')

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('bib','rider','race','team','dnf','val')
    list_filter = ('race','team')
    search_fields = ('rider__last_name',)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name','user','league')

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name','id','owner','is_classic','is_private')

class RiderAdmin(admin.ModelAdmin):
    list_display = ('last_name','first_name','id','country')

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','date','race')


admin.site.register(Race, RaceAdmin)
admin.site.register(Participation,ParticipationAdmin)
admin.site.register(Team,TeamAdmin)
admin.site.register(League,LeagueAdmin)
admin.site.register(Rider,RiderAdmin)
admin.site.register(Post,PostAdmin)