# Generated by Django 4.1.6 on 2023-02-07 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0003_rename_requester_meteoinfo_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meteoinfo',
            name='station',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, to='stations.station'),
        ),
    ]
