# Generated by Django 4.1.6 on 2023-02-08 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0009_alter_meteoinfo_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meteoinfo',
            name='date_time',
            field=models.DateTimeField(default='2023-02-08 15:30:44'),
        ),
    ]
