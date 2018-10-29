from django.shortcuts import get_object_or_404, render

from .models import Race

def index(request):
    # latest_races_list = Race.objects.order_by("-starts")
    latest_races_list = Race.objects.filter(is_classic=1).order_by("starts")
    context = {"latest_races_list": latest_races_list}
    return render(request, "races/index.html", context)

def detail(request,slug):
    race = get_object_or_404(Race,slug=slug)
    return render(request, "races/detail.html",{'race': race})