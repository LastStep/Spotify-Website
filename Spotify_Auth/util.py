from collections import defaultdict
from datetime import timedelta

import requests
from django.utils import timezone

from .credentials import CLIENT_ID, CLIENT_SECRET
from .firebase import DB_firebase as db

DB = db()


def api_request(request, url, data={}, params={}):
    token = get_token(request.session.get('username'))
    response = requests.get(url, 
                            headers={'Authorization': f'Bearer {token}'},
                            data=data,
                            params=params
                            )
    return response


def refresh_roken(user):
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': DB.get_user_data(
            user,
            collection='credentials',
            doc='creds',
            field='refresh_token')}, 
        auth=(CLIENT_ID, CLIENT_SECRET)).json()

    response['expires_in'] = timezone.now() + timedelta(seconds=response['expires_in'])
    DB.update_user_data(
        user,
        collection='credentials',
        doc='creds',
        dict_data=response)


def authenticate(user):
    DB.delete_user_data(user)


def is_authenticated(user):
    try:
        if DB.get_user_data(
            user,
            collection='credentials',
            doc='creds',
            field='expires_in') < timezone.now():
            refresh_roken(user)
        return True
    except (KeyError, TypeError):
        return False


def get_token(user):
    if is_authenticated(user):
        return DB.get_user_data(
            user,
            collection='credentials',
            doc='creds',
            field='access_token')


def get_user(request):
    return request.session.get('username')


def error_info(status_code):
    switches = {
        200: (True, None),
        201: (True, None),
        202: (True, None),

        204: (False, 'No Content'),

        400: (False, 'Bad Syntax'),
        401: (False, 'Unauthorized'),
        403: (False, 'Forbidden'),
        404: (False, 'Not Found'),
        429: (False, 'Too Many Requests'),

        502: (False, 'Bad Gateway'),
        503: (False, 'Service Unavailable')
    }
    return switches[status_code]



def update_playlist_id(request):
    url = 'https://api.spotify.com/v1/me/playlists'
    response = api_request(request, url, params={'limit':50})

    status, error = error_info(response.status_code)

    if status:
        data = response.json()
        playlist_ids = {str(k):item['id'] for k,item in enumerate(data['items'])}
        DB.update_user_data(
            get_user(request), 
            collection='playlist_data', 
            doc='playlist_id', 
            dict_data=playlist_ids)
    
    else:
        print(error)


def get_playlists(request):
    try:
        playlists = DB.get_user_data(
            get_user(request),
            collection='playlist_data',
            doc='playlist_id')
        # playlists = list(playlists.values())
        return playlists
    except Exception as e:
        print(f'Error in Getting Playlist from DB : {e}')
        return []


def store_playlists_data(request):
    pl_ids = get_playlists(request)
    pl_info = {}
    for pl_num, pl_id in pl_ids.items():
        url = f'https://api.spotify.com/v1/playlists/{pl_id}'
        response = api_request(request, url)
        status, error = error_info(response.status_code)

        info = {}
        if status:
            response = response.json()
            info['playlist_name'] = response['name']
            info['playlist_url'] = response['external_urls']['spotify']
            info['playlist_image'] = response['images'][0]['url']
        
        # pl_tracks = store_playlists_tracks(request, url, response['name'])
        # DB.update_user_collection_field(get_user(request), 'playlist_data', 'tracks', f'playlist_tracks.{str(pl_num)}', pl_tracks)

        pl_info[str(pl_num)] = info

    DB.update_user_data(
        get_user(request),
        collection='playlist_data',
        doc='playlist_info',
        dict_data=pl_info)
    


def get_playlists_data(request):
    try:
        return DB.get_user_data(
            get_user(request),
            collection='playlist_data',
            doc='playlist_info')
    except Exception as e:
        print(f'Error in Getting Playlist Data from DB : {e}')
        return False


def store_playlists_tracks(request, playlist_api_url, playlist_name, offset=0):
    url = f'{playlist_api_url}/tracks'
    response = api_request(request, url, params={
        'fields': 'items(track(name,external_urls,album(name,images,external_urls),artists(name,external_urls)))',
        'limit': 100,
        'offset': offset
    })

    status, error = error_info(response.status_code)

    tracks_data = []
    if status:
        data = response.json()

        for track in data['items']:
            try:
                track = track['track']
                track_info = defaultdict(list)
                track_info['playlist_name'] = playlist_name

                track_info['track_name'] = track['name']
                track_info['track_link'] = track['external_urls']['spotify']

                track_info['album_name'] = track['album']['name']
                track_info['album_link'] = track['album']['external_urls']['spotify']
                track_info['album_image'] = track['album']['images'][0]['url']

                for artist in track['artists']:
                    track_info['artist_name'].append(artist['name'])
                    track_info['artist_link'].append(artist['external_urls']['spotify'])

                tracks_data.append(track_info)
            except KeyError:
                pass

    return tracks_data
