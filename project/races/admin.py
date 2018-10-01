from django.contrib import admin

from .models import Race, Rider, Participation


class RaceAdmin(admin.ModelAdmin):
    list_display = ('name','starts')


admin.site.register(Race, RaceAdmin)
admin.site.register(Rider)
admin.site.register(Participation)