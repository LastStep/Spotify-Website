from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    remember_me = forms.BooleanField(required=False)

class ScanPlaylists(forms.Form):
    pass