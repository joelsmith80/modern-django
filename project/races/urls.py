from django.urls import path

from . import views

app_name = "races"
urlpatterns = [
    path("", views.index, name="index"),
    path("races/<slug:slug>/", views.detail, name="detail")
]