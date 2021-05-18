from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    remember_me = forms.BooleanField(required=False)


class SearchBox(forms.Form):
    search = forms.CharField(label=False, max_length=100,
                             widget=forms.TextInput(attrs={'placeholder': 'Song Name...'}))