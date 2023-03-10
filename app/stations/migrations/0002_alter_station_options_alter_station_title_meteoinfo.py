# Generated by Django 4.1.6 on 2023-02-07 09:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stations', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='station',
            options={'verbose_name': 'Метеостанция'},
        ),
        migrations.AlterField(
            model_name='station',
            name='title',
            field=models.CharField(default='', max_length=70, verbose_name='Название Станиций'),
        ),
        migrations.CreateModel(
            name='MeteoInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.JSONField()),
                ('date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('station', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='stations.station')),
            ],
            options={
                'verbose_name': 'Метеоданные',
            },
        ),
    ]
