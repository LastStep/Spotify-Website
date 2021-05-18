from django.urls import path
from . import views_auth
from . import views_pages


urlpatterns = [
    path('', views_auth.login_form),
    path('login', views_auth.login),
    path('login/redirect', views_auth.callback),

    path('welcome', views_pages.welcome),
    path('search_playlist', views_pages.search_playlist)
]
