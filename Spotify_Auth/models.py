from django.db import models


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
    playlist_id = models.TextField(primary_key=True)
    playlist_name = models.TextField()
    playlist_url = models.TextField()
    playlist_uri = models.TextField()
    playlist_total_tracks = models.IntegerField(null=True, blank=True)
    playlist_public = models.BooleanField(null=True, blank=True)
    playlist_image = models.TextField(null=True, blank=True)


    class Meta:
        db_table = 'playlist_info'