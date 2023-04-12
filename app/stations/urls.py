from django.urls import re_path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	re_path(r'api/', include("django.contrib.auth.urls")),
	re_path(r'^$', views.station_list, name="home"),
	re_path(r'^api/stations$', views.station_list, name="stations-list"),
	re_path(r'^api/stations/(?P<pk>[0-9]+)$', views.station_detail, name="station-detail"),
	re_path(r'^api/stations/', views.station_list, name="stations-list"),
	re_path(r'^api/meteoinfo$', views.meteoinfo_list, name="meteoinfo-list"),
	re_path(r'^api/meteoinfo/(?P<pk>[0-9]+)$', views.meteoinfo_detail, name="meteoinfo-detail"),
	re_path(r'^api/meteoinfo/', views.meteoinfo_list, name="meteoinfo-list"),
	re_path(r'^api/user$', views.user_list, name="user-list"),
	re_path(r'^api/user/(?P<pk>[0-9]+)$', views.user_detail, name="user-detail"),
	re_path(r'^api/user/', views.user_list, name="user-list"),
	# re_path(r'^api/stations/address$', views.station_list_published)
]
