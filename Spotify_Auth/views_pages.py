import json
from collections import defaultdict

from django.shortcuts import redirect, render

from . import util
from .database import DataBase
from .forms import ScanPlaylists
from .models import PlaylistData, TracksData

PLAYLIST_DB = DataBase(PlaylistData)
TRACKS_DB = DataBase(TracksData)

PLAYLIST_DATA = None
TRACKS_DATA = None


def welcome(request):
    url = 'https://api.spotify.com/v1/me/player/currently-playing'
    response = util.api_request(request, url)
    
    status, error = util.error_info(response.status_code)
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
    scanForm = ScanPlaylists(request.POST or None)
    title = 'Search Playlist'

    global PLAYLIST_DATA, TRACKS_DATA

    if PLAYLIST_DATA:
        playlist_data = PLAYLIST_DATA
    else:
        playlist_data = PLAYLIST_DATA = PLAYLIST_DB.get_data(
                filters={'username': request.session['username']},
                order=('playlist_name',)
            )
        
    ids = playlist_data.values_list('id', flat=True)

    if TRACKS_DATA:
        tracks_data = TRACKS_DATA
    else:
        tracks_data = TRACKS_DATA = TRACKS_DB.get_data(
            filters={'playlist_id__in': ids},
            related='playlist',
            as_query=True,
        )
    tracks_list = json.dumps(list(tracks_data.values_list('track_name', flat=True).distinct()))

    if post_data := request.POST:
        if post_data.get('scanForm'):
            util.update_playlist_id(request)
            util.store_playlists_data(request)
            scanBtnClass = 'btn btn-success'

        if post_data.get('searchForm'):
            search = post_data.get('searchForm')
            search_tracks = tracks_data.filter(track_name__contains=search)

            return render(request, 'search_playlist.html', locals())
                       
    
    return render(request, 'search_playlist.html', locals())

