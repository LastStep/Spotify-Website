from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from . import util
from .forms import SearchBox, ScanPlaylists


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
    searchForm, scanForm = SearchBox(request.POST or None), ScanPlaylists(request.POST or None)
    context = {
        'title': 'Search Playlist',
        'searchForm': searchForm,
        'scanForm': scanForm,
    }

    if request.method == 'POST':
        if scanForm.is_valid():
            util.update_playlist_id(request)
            util.store_playlists_data(request)
            context['scanBtnClass'] = 'btn btn-success'
            # return render(request, 'search_playlist.html', context=context)

        # if searchForm.is_valid():
        #     request.session['search'] = searchForm.cleaned_data['search']
        #     context = {
        #         'title': 'Search Playlist',
        #         'search': request.session.get('search'),
        #         'form': searchForm
        #     }
        #     return render(request, 'search_playlist.html', context=context)

    pl_data = util.get_playlists_data(request)
    if pl_data:
        context['playlist_data'] = pl_data
        # context['playlist_data'] = sorted(zip(
        #     pl_data['playlist_names'],
        #     pl_data['playlist_urls'],
        #     pl_data['playlist_imgs'],
        # ))

    return render(request, 'search_playlist.html', context=context)

