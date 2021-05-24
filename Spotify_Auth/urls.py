from django.urls import path
from . import views_auth
from . import views_pages

app_name = 'main'

urlpatterns = [
    path('', views_auth.login_form),
    path('login', views_auth.login),
    path('login/redirect', views_auth.callback),

    path('welcome', views_pages.welcome, name='home'),
    path('search_playlist', views_pages.search_playlist, name='playlists'),
]
