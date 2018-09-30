from django.urls import path

from . import views

app_name = "races"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:id>/", views.detail, name="detail")
]