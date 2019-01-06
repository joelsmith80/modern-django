from django.urls import path

from . import views

app_name = 'races'
urlpatterns = [
    path('', views.home, name='home'),
    path('race/<slug:slug>/', views.race_show, name='race_show'),
    path('leagues', views.leagues_index, name='leagues_index'),
    path('league/<int:id>/', views.league_show, name='league_show'),
    path('teams', views.teams_index, name='teams_index'),
    path('team/<int:id>/', views.team_show, name='team_show'),
    path('team/<int:id>/race/<slug:slug>/', views.team_race, name='team_race'),
    path('rider/<int:id>/', views.rider_show, name='rider_show')
]