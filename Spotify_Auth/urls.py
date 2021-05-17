from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_form),
    path('login', views.authURL),
    path('login/redirect', views.callback),

    path('welcome', views.welcome)
]
