from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room, User
from .serializers import *

@api_view(['GET'])
def get_routes(request):
  routes = [
    'GET /api'
    'GET /api/rooms',
    'GET /api/rooms/:id',
    'GET /api/users',
    'GET /api/users/:id',
  ]
  return Response(routes)

@api_view(['GET'])
def get_rooms(request):
  rooms = Room.objects.all()
  serializer = RoomSerializer(rooms, many=True)
  return Response(serializer.data)

@api_view(['GET'])
def get_room(request, id):
  room = Room.objects.get(id=id)
  serializer = RoomSerializer(room, many=False)
  return Response(serializer.data)

@api_view(['GET'])
def get_users(request):
  users = User.objects.all()
  serializer = RoomSerializer(users, many=True)
  return Response(serializer.data)

@api_view(['GET'])
def get_user(request, id):
  user = User.objects.get(id=id)
  serializer = RoomSerializer(user, many=False)
  return Response(serializer.data)
