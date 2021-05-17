from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

import requests
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE

from .forms import LoginForm
from DataBase.firebase import DB_firebase as db
from .util import get_token


DB = db()



def welcome(request):
    token = get_token(request.session.get('username'))
    data = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers={
        'Authorization': f'Bearer {token}'
    }).json()
    context = {
        'username': request.session.get('username'),
        'token': token,
        'data': data
    }
    return render(request, 'welcome.html', context=context)


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

    DB.set_user_data(request.session.get('username'), response)
    return redirect('/welcome')



def login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.session['username'] = form.cleaned_data['username']
            # request.session['db'] = db

            # if DB.if_doc_exists(form.cleaned_data['username']):
            #     return HttpResponseRedirect('/welcome')
            return HttpResponseRedirect('/login')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
