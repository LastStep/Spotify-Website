# Generated by Django 3.2.3 on 2021-06-12 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Spotify_Auth', '0003_database_playlist_data'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='credentials',
            table='credentials',
        ),
    ]