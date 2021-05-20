import requests, json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from .util import api_request, error_handling, update_playlist_api_urls
from .forms import SearchBox


def welcome(request):
    url = 'https://api.spotify.com/v1/me/player/currently-playing'
    response = api_request(request, url)
    
    status, error = error_handling(response.status_code)
    context = {
        'username': request.session.get('username'),
        'title': 'Welcome'
    }

    if status:
        context['data'] = response.json()
        context['title'] = response.json()['item']['name']
        # context['favicon_url'] = response.json()['item']['album']['images'][1]['url']
    else:
        context['error'] = error
    return render(request, 'welcome.html', context=context)


def search_playlist(request):
    update_playlist_api_urls(request, request.session.get('username'))

    if request.method == 'POST':
        form = SearchBox(request.POST)
        if form.is_valid():
            request.session['search'] = form.cleaned_data['search']
            context = {
                'title': 'Search Playlist',
                'search': request.session.get('search'),
                'form': form
            }
            return render(request, 'search_playlist.html', context=context)

    else:
        form = SearchBox()

    context = {
        'title': 'Search Playlist',
        'form': form
    }

    return render(request, 'search_playlist.html', context=context)