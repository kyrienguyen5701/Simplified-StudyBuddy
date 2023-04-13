from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm

# Create your views here.
def home(request):
  q = ''
  if request.GET.get('q'):
    q = request.GET.get('q')
  rooms = Room.objects.filter(
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
  )
  topics = Topic.objects.all()[:5]
  room_count = rooms.count() # faster than len
  ctx = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
  return render(request, 'base/home.html', ctx)

def room(request, id):
  room = Room.objects.get(id=id)
  ctx = {'room': room}
  return render(request, 'base/room.html', ctx)

def create_room(request):
  form = RoomForm()

  if request.method == 'POST':
    # get content from request to fill the form
    form = RoomForm(request.POST)

    # check if the form is valid, save, and redirect
    if form.is_valid():
      form.save()
      return redirect('home')

  ctx = {'form': form}
  return render(request, 'base/room_form.html', ctx)

def update_room(request, id):
  room = Room.objects.get(id=id)

  # prefill the form
  form = RoomForm(instance=room)

  if request.method == 'POST':
    # what room to update
    form = RoomForm(request.POST, instance=room)

    if form.is_valid():
      form.save()
      return redirect('home')

  ctx = {'room': room}
  return render(request, 'base/room_form.html', ctx)

def delete_room(request, id):
  room = Room.objects.get(id=id)
  if request.method == 'POST':
    room.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': room})
