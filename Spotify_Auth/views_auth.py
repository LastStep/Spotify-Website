from datetime import timedelta

import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils import timezone

from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE
from .firebase import DB_firebase as db
from .forms import LoginForm

DB = db()


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
    response['expires_in'] = timezone.now() + timedelta(minutes=5, seconds=response['expires_in'])

    DB.set_user_data(request.session.get('username'), response)
    return redirect('/welcome')



def login_form(request):
    if request.session.get('username'):
        return HttpResponseRedirect('/welcome')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['username'] = form.cleaned_data['username']
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)

            if DB.if_doc_exists(form.cleaned_data['username']):
                return HttpResponseRedirect('/welcome')
            return HttpResponseRedirect('/login')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
    

