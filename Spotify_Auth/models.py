from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import TextField


class Credentials(models.Model):

    username = models.CharField(max_length=50, primary_key=True)
    access_token = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    scope = models.TextField()
    token_type = models.TextField()
    expires_in = models.DateTimeField()

    class Meta:
        db_table = 'credentials'


class PlaylistData(models.Model):

    username = models.ForeignKey(
        Credentials,
        on_delete=models.CASCADE,
    )
    playlist_id = models.TextField()
    playlist_name = models.TextField()
    playlist_url = models.TextField()
    playlist_uri = models.TextField()
    playlist_total_tracks = models.IntegerField(null=True, blank=True)
    playlist_public = models.BooleanField(null=True, blank=True)
    playlist_image = models.TextField(null=True, blank=True)


    class Meta:
        db_table = 'playlist_data'



class TracksData(models.Model):

    # user = models.ForeignKey(
    #     Credentials,
    #     on_delete=models.CASCADE,
    # )
    playlist = models.ForeignKey(
        PlaylistData,
        on_delete=models.CASCADE,
    )
    track_name = models.TextField()
    track_link = models.TextField()
    album_name = models.TextField()
    album_link = models.TextField()
    album_image = models.TextField()
    artist_name = ArrayField(models.TextField())
    artist_link = ArrayField(models.TextField())


    class Meta:
        db_table = 'tracks_data'
