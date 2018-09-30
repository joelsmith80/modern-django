from django.shortcuts import get_object_or_404, render

from .models import Race

def index(request):
    latest_races_list = Race.objects.order_by("-created_at")[:5]
    context = {"latest_races_list": latest_races_list}
    return render(request, "races/index.html", context)

def detail(request,id):
    race = get_object_or_404(Race,pk=id)
    return render(request, "races/detail.html",{'race': race})