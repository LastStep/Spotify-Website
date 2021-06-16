from collections import defaultdict
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

import requests
from django.utils import timezone

from .credentials import CLIENT_ID, CLIENT_SECRET
from .models import Credentials, PlaylistData, TracksData
from .database import DataBase


CREDS_DB = DataBase(Credentials)
PLAYLIST_DB = DataBase(PlaylistData)
TRACKS_DB = DataBase(TracksData)


def api_request(request, url: str, data: dict = {}, params: dict = {}) -> requests.Response:
    token = get_token(get_user(request))
    return requests.get(url, 
                        headers={'Authorization': f'Bearer {token}'},
                        data=data,
                        params=params
                    )


def refresh_token(user: str):
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': CREDS_DB.get_data(
            filters= {'username': user}
            )[0]['refresh_token']
        }, 
        auth=(CLIENT_ID, CLIENT_SECRET)).json()

    response['expires_in'] = timezone.now() + timedelta(seconds=response['expires_in'])

    CREDS_DB.update_data(
        filters={'username':user},
        data=response
    )   


def is_authenticated(user: str) -> bool:
    creds = CREDS_DB.get_data(filters={'username': user})
    if len(creds):
        if creds[0]['expires_in'] <= timezone.now():
            refresh_token(user)
        return True
    else:
        return False



def get_token(user: str) -> str:
    if is_authenticated(user):
        try:
            return CREDS_DB.get_instance(
                filters={'username': user}
            ).access_token
        except ObjectDoesNotExist:
            print('Couldnt get Token')
            return False
    # else:
    #     authenticate()


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
        503: (False, 'Service Unavailable'),
    }
    return switches[status_code]


def update_playlist_id(request):
    url = 'https://api.spotify.com/v1/me/playlists'
    response = api_request(request, url, params = {'limit': 50})

    status, error = error_info(response.status_code)

    if status:
        user = get_user(request)
        for item in response.json()['items']:
            PLAYLIST_DB.update_or_create(
                data={
                    'playlist_name': item['name'],
                    'playlist_url': item['external_urls']['spotify'],
                    'playlist_uri': item['uri'],
                    'playlist_total_tracks': item['tracks']['total'],
                    'playlist_public': item['public'],
                    'playlist_image': item['images'][0]['url'],
                    'username': CREDS_DB.get_instance(filters={'username': user})
                },
                filters={
                    'playlist_id': item['id'],
                }
            )
    else:
        print(error)


def get_playlists(request) -> list:
    try:
        return PLAYLIST_DB.get_data(
            filters={'username': get_user(request)},
            fields=('playlist_id',),
            as_list=True,
            flat=True
        )
    except Exception as e:
        print(f'Error in Getting Playlist from DataBase : {e}')
        return []


def store_playlists_data(request):
    pl_ids = get_playlists(request)
    for pl_num, pl_id in enumerate(pl_ids):

        tracks_data = store_playlists_tracks(request, playlist_id=pl_id)
        for track_data in tracks_data:
            TRACKS_DB.update_or_create(
                filters={
                    'track_name': track_data.pop('track_name'),
                    'playlist': PLAYLIST_DB.get_instance(filters={'playlist_id': pl_id}),
                },
                data=track_data
            )


def store_playlists_tracks(request, playlist_id: str, offset: int = 0) -> list[dict]:
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    response = api_request(
        request, 
        url, 
        params={
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


