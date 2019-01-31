from django.contrib import admin

from .models import Race, Rider, Participation, Team, League, Post, Roster, SiteOption


class ParticipationInline(admin.TabularInline):
    model = Participation
    fields = ['rider','bib','squad','val']
    extra = 1

class RaceAdmin(admin.ModelAdmin):
    list_display = ('name','slug','starts','is_live','is_locked')
    inlines = (ParticipationInline,)

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('bib','rider','race','squad','dnf','val')
    list_filter = ('race','squad')
    search_fields = ('rider__last_name',)
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
    list_display = ('name','user','league')
    inlines = (RosterInline,)

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name','id','owner','is_classic','is_private')

class RiderAdmin(admin.ModelAdmin):
    list_display = ('full_name','id','country')
    search_fields = ('last_name',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','date','race')

class OptionAdmin(admin.ModelAdmin):
    list_display = ('opt_key','opt_value')

class RosterAdmin(admin.ModelAdmin):
    list_display = ('team','race')
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

admin.site.register(Race, RaceAdmin)
admin.site.register(Participation,ParticipationAdmin)
admin.site.register(Team,TeamAdmin)
admin.site.register(League,LeagueAdmin)
admin.site.register(Rider,RiderAdmin)
admin.site.register(Post,PostAdmin)
admin.site.register(Roster,RosterAdmin)
admin.site.register(SiteOption,OptionAdmin)