from django.contrib import admin

from .models import Race, Rider, Participation, Team, League


class RaceAdmin(admin.ModelAdmin):
    list_display = ('name','starts')

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('bib','rider','race','team','dnf','val')
    list_filter = ('race','team')
    search_fields = ('rider__last_name',)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name','user','league')

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name','race','owner','is_private')


admin.site.register(Race, RaceAdmin)
admin.site.register(Rider)
admin.site.register(Participation,ParticipationAdmin)
admin.site.register(Team,TeamAdmin)
admin.site.register(League,LeagueAdmin)