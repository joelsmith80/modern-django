from django.contrib import admin

from .models import Race, Rider, Participation


class RaceAdmin(admin.ModelAdmin):
    list_display = ('name','starts')

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('bib','rider','race','team','dnf','val')
    list_filter = ('race','team')
    search_fields = ('rider__last_name',)


admin.site.register(Race, RaceAdmin)
admin.site.register(Rider)
admin.site.register(Participation,ParticipationAdmin)