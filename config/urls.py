from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('', include('project.races.urls')),
    # path(r'^api/', include('project.api.urls')),
]