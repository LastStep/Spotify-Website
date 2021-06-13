from collections import defaultdict
from django.shortcuts import redirect, render

from . import util
from .forms import ScanPlaylists
from .models import PlaylistData
from .database import DataBase

PLAYLIST_DATA = DataBase(PlaylistData)


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

    if request.POST:
        if scanForm.is_valid():
            util.update_playlist_id(request)
            # util.store_playlists_data(request)
            scanBtnClass = 'btn btn-success'

        if request.POST.get('searchForm'):
            search = request.session['search'] = request.POST.get('searchForm')
            search_result = defaultdict(list)
            for playlist_id, tracks in request.session['songs_data'].items():
                for track in tracks:
                    if search == track['track_name']:
                        search_result[playlist_id].append(track)
            search_result = dict(search_result)

    playlist_data = PLAYLIST_DATA.get_data(
        filters={'username': request.session['username']},
        order=('playlist_name',)
    )

    # try:
    #     songs_data = request.session['songs_data']
    #     songs_list = request.session['songs_list']
    # except KeyError:
    #     tracks_dict = util.get_tracks(request)
    #     songs_data = request.session['songs_data'] = tracks_dict

    #     songs_list = defaultdict(bool)
    #     for playlist_id, tracks in tracks_dict.items():
    #         for track in tracks:
    #             songs_list[track['track_name']] = True
    #     songs_list = request.session['songs_list'] = json.dumps(songs_list)
    
    return render(request, 'search_playlist.html', locals())

