from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('',include('app.urls')),
    path('superuser/admin/', admin.site.urls),
]
