from datetime import timedelta

import requests
from DataBase.firebase import DB_firebase as db
from django.utils import timezone

from .credentials import CLIENT_ID, CLIENT_SECRET

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
        'refresh_token': DB.get_user_data_field(user, 'refresh_token')}, 
        auth=(CLIENT_ID, CLIENT_SECRET)).json()

    response['expires_in'] = timezone.now() + timedelta(minutes=5, seconds=response['expires_in'])
    DB.update_user_data(user, response)


def is_authenticated(user):
    if DB.get_user_data_field(user, 'expires_in') < timezone.now():
        refresh_roken(user)


def get_token(user):
    is_authenticated(user)
    return DB.get_user_data_field(user, 'access_token')


def error_handling(status_code):
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


def update_playlist_api_urls(request, user):
    url = 'https://api.spotify.com/v1/me/playlists'
    response = api_request(request, url, params={'limit':50})

    status, error = error_handling(response.status_code)

    if status:
        data = response.json()
        playlist_urls = []
        for item in data['items']:
            playlist_urls.append(item['tracks']['href'])

        DB.update_user_data(user, {'playlist_api_urls':playlist_urls})

