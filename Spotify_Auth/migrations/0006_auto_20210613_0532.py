# Generated by Django 3.2.3 on 2021-06-13 00:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Spotify_Auth', '0005_auto_20210612_1216'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaylistData',
            fields=[
                ('playlist_id', models.IntegerField(primary_key=True, serialize=False)),
                ('playlist_name', models.TextField()),
                ('playlist_url', models.TextField()),
                ('playlist_uri', models.TextField()),
                ('playlist_total_tracks', models.IntegerField(blank=True, null=True)),
                ('playlist_public', models.BooleanField(blank=True, null=True)),
                ('playlist_image', models.TextField(blank=True, null=True)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Spotify_Auth.credentials')),
            ],
            options={
                'db_table': 'playlist_info',
            },
        ),
        migrations.DeleteModel(
            name='Playlist_Data',
        ),
    ]