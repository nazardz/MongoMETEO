# Generated by Django 4.1.6 on 2023-02-07 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_alter_station_options_alter_station_title_meteoinfo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meteoinfo',
            old_name='requester',
            new_name='author',
        ),
    ]