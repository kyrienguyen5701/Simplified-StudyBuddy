from django.urls import path
from . import views

urlpatterns = [
  path('', views.get_routes),
  path('rooms/', views.get_rooms),
  path('room/<str:id>/', views.get_room),
  path('users/', views.get_users),
  path('users/<str:id>/', views.get_user),
]
