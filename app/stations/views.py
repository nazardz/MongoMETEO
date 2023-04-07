from django.shortcuts import render
import requests
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from .models import Station, MeteoInfo
from django.contrib.auth.models import User
from .serializers import StationSerializer, MeteoInfoSerializer, MeteoInfoRequestSerializer, UserSerializer, \
	UserStationsUpdateSerializer, NewUserSerializer
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

TIMEOUT = 5
PERMISSION_DENIED = JsonResponse({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
# add login redirection


def get_meteoinfo(url):
	full_url = "http://{}".format(url)
	response = {'msg': f"Cтанция {url} недоступна. Поробуйте еще раз", 'code': 0}
	try:
		r = requests.get(full_url, timeout=TIMEOUT)
		if r.status_code == 200:
			response['msg'] = r.json()
			response['code'] = 1
	except requests.exceptions.ReadTimeout:
		pass
	except requests.exceptions.ConnectTimeout:
		pass
	except requests.exceptions.InvalidSchema:
		response['msg'] = f"Неправильный адрес."
	except requests.exceptions.ConnectionError:
		response['msg'] = f"Cтанция {url} выключена."
	# except requests.exceptions.MissingSchema:
	#    response['msg'] = f"Невозможный адресс станций."
	return response


def username_exists(username):
	return User.objects.filter(username=username)


# --STATIONS------------------------------------------------------------------------------------------------------------
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def station_list(request):
	# GET list of stations, POST a new station, DELETE all stations

	# permission for staff and superusers
	if not request.user.is_superuser or not request.user.is_staff:
		return PERMISSION_DENIED

	if request.method == 'GET':
		elements = Station.objects.all()
		title = request.GET.get('title', None)
		if title is not None and title != '':
			elements = elements.filter(title__icontains=title)
		serializer = StationSerializer(elements, many=True)
		return JsonResponse({"count": len(elements), "data": serializer.data}, safe=False)
		# 'safe=False' for objects serialization
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = StationSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			users = User.objects.all()
			# superusers = users.filter(is_superuser=True)
			# staff = users.filter(is_staff=True)
			# users = superusers | staff
			for user in users:
				if user.is_superuser or user.is_staff:
					user.stations_whitelist.add(serializer.data['id'])
					user.save()
			return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
		return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		count = Station.objects.all().delete()
		return JsonResponse({'message': '{} Stations were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def station_detail(request, pk):
	# find station by pk (id)
	try:
		element = Station.objects.get(pk=pk)
	except Station.DoesNotExist:
		return JsonResponse({'message': 'The station does not exist'}, status=status.HTTP_404_NOT_FOUND)

	# permission for staff and superusers
	if not request.user.is_superuser or not request.user.is_staff :
		return PERMISSION_DENIED

	# GET / PUT / DELETE station
	if request.method == 'GET':
		serializer = StationSerializer(element)
		return JsonResponse(serializer.data)
	elif request.method == 'PUT':
		station_data = JSONParser().parse(request)
		serializer = StationSerializer(element, data=station_data)
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(serializer.data)
		return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		element.delete()
		return JsonResponse({'message': 'Station was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


# --METEOINFO-----------------------------------------------------------------------------------------------------------
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def meteoinfo_list(request):
	# GET list of meteoinfo, POST a new meteoinfo, DELETE all meteoinfo
	user = request.user
	if request.method == 'GET':
		elements = MeteoInfo.objects.all()
		# filter_author = request.GET.get('author', None)
		filter_station = request.GET.get('station', None)

		if not request.user.is_superuser or not request.user.is_staff:
			current_user = User.objects.get(pk=request.user.id)
			user_serializer = UserSerializer(current_user)
			access_stations = user_serializer.data["stations_whitelist"]
			# elements = elements.filter(Q(author=current_user) | Q(station__in=access_stations))
			elements = elements.filter(Q(station__in=access_stations))

		# author filter
		# if filter_author is not None and filter_author != '':
		# 	elements = elements.filter(author=filter_author)
		# station filter
		if filter_station is not None and filter_station != '':
			elements = elements.filter(station=filter_station)

		serializer = MeteoInfoSerializer(elements, many=True)
		return JsonResponse({"count": len(elements), "data": serializer.data}, safe=False)
		# 'safe=False' for objects serialization
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = MeteoInfoRequestSerializer(data=data)

		if serializer.is_valid():
			initial_data = serializer.initial_data
			station = Station.objects.get(pk=initial_data['station'])

			try:
				if station != user.stations_whitelist.get(id=station.id):
					return PERMISSION_DENIED
			except Station.DoesNotExist:
				return JsonResponse({'message': "User doesn't have access to station {}".format(station.id)}, status=status.HTTP_403_FORBIDDEN)

			content = get_meteoinfo(station.address)
			if content['code'] == 1:
				new_content = {
					'station': initial_data['station'],
					'content': content['msg'],
					# 'author': user.id,
				}
				new_serializer = MeteoInfoSerializer(data=new_content)
				if new_serializer.is_valid():
					new_serializer.save()
					user.info_requests_count = user.info_requests_count or 0
					user.info_requests_count += 1

					# user.meteo_infos.add(new_serializer.data['id'])
					user.save()
					return JsonResponse(new_serializer.data, status=status.HTTP_201_CREATED)

			return JsonResponse(content['msg'], status=status.HTTP_400_BAD_REQUEST)
		return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		if not user.is_superuser or not user.is_staff:
			return PERMISSION_DENIED
		count = MeteoInfo.objects.all().delete()
		return JsonResponse({'message': '{} Meteoinfos were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def meteoinfo_detail(request, pk):
	# find station by pk (id)
	try:
		element = MeteoInfo.objects.get(pk=pk)
	except MeteoInfo.DoesNotExist:
		return JsonResponse({'message': 'The meteoinfo does not exist'}, status=status.HTTP_404_NOT_FOUND)

	if not request.user.is_superuser or not request.user.is_staff:
		current_user = User.objects.get(pk=request.user.id)
		user_serializer = UserSerializer(current_user)
		access_stations = user_serializer.data["stations_whitelist"]

		if element.station.pk not in access_stations:
			# if element.author.pk != request.user.id:
			return PERMISSION_DENIED

	# GET / DELETE station
	if request.method == 'GET':
		serializer = MeteoInfoSerializer(element)
		return JsonResponse(serializer.data)

	elif request.method == 'DELETE':
		if not request.user.is_superuser or not request.user.is_staff:
			return PERMISSION_DENIED
		element.delete()
		return JsonResponse({'message': 'Meteoinfo was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


# -USERS----------------------------------------------------------------------------------------------------------------
@api_view(['GET', 'POST'])  # , 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
	# GET list of users, POST a new user, ## DELETE all users
	# user = request.user

	if request.method == 'GET':
		elements = User.objects.all()
		serializer = UserSerializer(elements,  many=True)
		return JsonResponse({"count": len(elements), "data": serializer.data}, safe=False)
		# 'safe=False' for objects serialization
	elif request.method == 'POST':
		data = JSONParser().parse(request)


		if username_exists(data['username']):
			return JsonResponse({'message': "User '"+data['username']+"' already exist"}, status=status.HTTP_400_BAD_REQUEST)

		if len(data['stations_whitelist']) == 0:
			data['stations_whitelist'] = [1]
		serializer = NewUserSerializer(data=data)
		if serializer.is_valid():
			initial_data = serializer.initial_data
			if request.user.is_superuser or request.user.is_staff:
				user = User.objects.create_user(username=initial_data['username'],
				                                email=initial_data['email'],
				                                password=initial_data['password'])

				for station in initial_data['stations_whitelist']:
					user.stations_whitelist.add(station)
				user.info_requests_count = 0
				user.save()
				serial = UserSerializer(user)
				return JsonResponse({'message': "New user succesfully added", "data": serial.data}, safe=False)
			else:
				return PERMISSION_DENIED

	return JsonResponse({'message': "400 BAD REQUEST"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request, pk):
	# find station by pk (id)

	try:
		element = User.objects.get(pk=pk)
	except User.DoesNotExist:
		return JsonResponse({'message': 'The user does not exist'}, status=status.HTTP_404_NOT_FOUND)

	# GET / PUT / DELETE station
	if request.method == 'GET':
		serializer = UserSerializer(element)
		return JsonResponse(serializer.data)
	if request.method == 'PUT':
		if not request.user.is_superuser or not request.user.is_staff:
			return PERMISSION_DENIED

		data = JSONParser().parse(request)
		serializer = UserStationsUpdateSerializer(data=data)
		if serializer.is_valid():

			try:
				add_stations_list = data['add_station']
			except KeyError:
				add_stations_list = []

			try:
				remove_station_list = data['remove_station']
			except KeyError:
				remove_station_list = []

			user_stations = element.stations_whitelist
			if add_stations_list:
				for station_id in add_stations_list:
					try:
						if user_stations.get(id=station_id):
							pass
					except Station.DoesNotExist:
						try:
							if Station.objects.get(pk=station_id):
								element.stations_whitelist.add(station_id)
						except Station.DoesNotExist:
							return JsonResponse({'message': '{} - station does not exist'.format(station_id)}, status=status.HTTP_404_NOT_FOUND)
			if remove_station_list:
				for station_id in remove_station_list:
					try:
						if user_stations.get(id=station_id):
							element.stations_whitelist.remove(station_id)
					except Station.DoesNotExist:
						try:
							if Station.objects.get(pk=station_id):
								pass
						except Station.DoesNotExist:
							return JsonResponse({'message': '{} - station does not exist'.format(station_id)},status=status.HTTP_404_NOT_FOUND)
			element.save()
			serializer = UserSerializer(element)
			return JsonResponse(serializer.data)
		return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	elif request.method == 'DELETE':

		if pk == "1":
			return JsonResponse({'message': 'Root can not be deleted!'}, status=status.HTTP_204_NO_CONTENT)
		elif not request.user.is_superuser or not request.user.is_staff:  #request.user != element or
			return PERMISSION_DENIED
		element.delete()
		return JsonResponse({'message': 'User was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

"""
@api_view(['GET'])
def station_list_published(request):
	# GET address stations
	stations = MeteoInfo.objects.filter(published=True)

	if request.method == 'GET':
		stations_serializer = StationSerializer(stations, many=True)
		return JsonResponse(stations_serializer.data, safe=False)
"""