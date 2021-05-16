from django.urls import path
from . import views


urlpatterns = [
    path('', views.authURL),
    path('home', views.home),
    path('redirect', views.callback),
]
