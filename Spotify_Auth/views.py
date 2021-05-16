from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from rest_framework.views import APIView

from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE
import requests


def home(request):
    return HttpResponse('Home')


def authURL(request):
    url = requests.Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': SCOPE,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url
    return HttpResponseRedirect(url)



def callback(request):
    code = request.GET.get('code')
    
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    print(response)
    return redirect('/login/home')




