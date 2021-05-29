from collections import defaultdict
from django.shortcuts import redirect, render

from . import util
from .forms import ScanPlaylists

import json


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
    context = {
        'title': 'Search Playlist',
        'scanForm': scanForm,
    }

    if request.method == 'POST':
        if scanForm.is_valid():
            util.update_playlist_id(request)
            util.store_playlists_data(request)
            context['scanBtnClass'] = 'btn btn-success'

        if request.POST.get('searchForm'):
            search = context['search'] = request.session['search'] = request.POST.get('searchForm')
            search_result = defaultdict(list)
            for playlist_id, tracks in request.session['songs_data'].items():
                for track in tracks:
                    if search == track['track_name']:
                        search_result[playlist_id].append(track)
            context['search_result'] = dict(search_result)

    try:
        context['playlist_data'] = dict(request.session['playlist_data'])
    except KeyError:
        context['playlist_data'] = request.session['playlist_data'] = dict(util.get_playlists_data(request))

    try:
        context['songs_data'] = request.session['songs_data']
        context['songs_list'] = request.session['songs_list']
    except KeyError:
        tracks_dict = util.get_tracks(request)
        context['songs_data'] = request.session['songs_data'] = tracks_dict

        songs_list = defaultdict(bool)
        for playlist_id, tracks in tracks_dict.items():
            for track in tracks:
                songs_list[track['track_name']] = True
        context['songs_list'] = request.session['songs_list'] = json.dumps(songs_list)
    
    return render(request, 'search_playlist.html', context=context)

