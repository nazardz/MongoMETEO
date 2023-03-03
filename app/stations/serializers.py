from rest_framework import serializers
from .models import Station, MeteoInfo
from django.contrib.auth.models import User


class StationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Station
		fields = ('id',
		          'title',
		          'description',
		          'address')


class MeteoInfoRequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = MeteoInfo
		fields = ('id',
		          'station',)


class MeteoInfoSerializer(serializers.ModelSerializer):
	class Meta:
		model = MeteoInfo
		fields = ('id',
		          'station',
		          'content',
		          'date_time',
		          #'author',
		          )


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id',
		          'username',
		          'info_requests_count',
		          'stations_whitelist',
		          #'meteo_infos',
		          )


class UserStationsUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id',
		          )


class NewUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username',
		          'password',
		          'email',
		          'stations_whitelist',
		          )
