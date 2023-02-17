from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Station(models.Model):
    title = models.CharField('Название Станиций', max_length=70, blank=False, default='')
    description = models.CharField(max_length=200, blank=False, default='')
    address = models.CharField(max_length=25, blank=False, default='')

    def __str__(self):
        return self.title or ""  # title

    def get_absolute_url(self):
        return reverse('station-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Метеостанция'

class MeteoInfo(models.Model):
    station = models.ForeignKey(Station, on_delete=models.SET_DEFAULT, default=0)
    content = models.JSONField()
    current_datetime = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
    date_time = models.DateTimeField(default=current_datetime)
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=0)


    def __str__(self):
        return reverse('meteoinfo-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Метеоданные'


User.add_to_class('info_requests_count', models.IntegerField(default=0))
User.add_to_class('stations_whitelist', models.ManyToManyField(Station, default=0))
User.add_to_class('meteo_infos', models.ManyToManyField(MeteoInfo, default=0, editable=False))