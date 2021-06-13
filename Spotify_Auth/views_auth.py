from datetime import timedelta

import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils import timezone

from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE
from .forms import LoginForm
from .util import is_authenticated
from .models import Credentials
from .database import DataBase


def login(request):
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
    response['expires_in'] = timezone.now() + timedelta(seconds=response['expires_in'])

    creds = DataBase(Credentials)
    creds.update_or_create(
        filters={'username': request.session['username']}, 
        data=response
    )
    return redirect('/welcome')



def login_form(request):
    user = request.session.get('username')
    # if user and DB.if_doc_exists(user) and is_authenticated(user):
    #     return HttpResponseRedirect('/welcome')


    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            request.session['username'] = user
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)

            # if DB.if_doc_exists(user):
            #     if is_authenticated(user):
            #         return HttpResponseRedirect('/welcome')
            #     authenticate(user)
                
            return HttpResponseRedirect('/login')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
    

