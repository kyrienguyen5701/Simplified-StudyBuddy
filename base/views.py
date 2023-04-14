from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

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

  # get recent activities only for the current room in view
  recent_activities = Message.objects.filter(Q(room__topic__name__icontains=q))
  
  ctx = {
    'rooms': rooms,
    'topics': topics,
    'room_count': room_count,
    'recent_activities': recent_activities
  }
  return render(request, 'base/home.html', ctx)

def room(request, id):
  room = Room.objects.get(id=id)
  msgs = room.message_set.all()
  participants = room.participants.all()

  if request.method == 'POST':
    msg = Message.objects.create(
      user=request.user,
      room=room,
      content=request.POST.get('content')
    )

    # add a new user once they comment
    room.participants.add(request.user)

    return redirect('room', id=room.id)
  
  ctx = {
    'room': room,
    'msgs': msgs,
    'participants': participants
  }
  return render(request, 'base/room.html', ctx)

@login_required(login_url='login')
def create_room(request):
  form = RoomForm()

  if request.method == 'POST':
    # get content from request to fill the form
    form = RoomForm(request.POST)

    # check if the form is valid, save, and redirect
    if form.is_valid():
      room = form.save(commit=False)
      room.host = request.user
      room.save()
      return redirect('home')

  ctx = {
    'form': form
  }
  return render(request, 'base/room_form.html', ctx)

@login_required(login_url='login')
def update_room(request, id):
  room = Room.objects.get(id=id)

  # prefill the form
  form = RoomForm(instance=room)

  topics = Topic.objects.all()

  if request.user != room.host:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, _ = Topic.objects.get_or_create(name=topic_name)
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()
    return redirect('home')

  ctx = {
    'room': room,
    'form': form,
    'topics': topics
  }
  return render(request, 'base/room_form.html', ctx)

@login_required(login_url='login')
def delete_room(request, id):
  room = Room.objects.get(id=id)

  if request.user != room.host:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    room.delete()
    return redirect('home')
  
  ctx = {
    'obj': room
  }
  return render(request, 'base/delete.html', ctx)

def login_page(request):
  page = 'login'
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == 'POST':
    # get info
    username = request.POST.get('username').lower()
    password = request.POST.get('password')
    
    # check if user exists
    try:
      user = User.objects.get(username=username)
    except:
      messages.error(request, 'User not found!')
    
    # authenticate and login
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'Username or password does not match.')

  ctx = {'page': page}
  return render(request, 'base/login_register.html', ctx)

def logout_user(request):
  logout(request)
  return redirect('home')

def register_page(request):
  form = UserCreationForm()
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # does not save the user to the db yet
      user = form.save(commit=False)

      # clean data
      user.username = user.username.lower()

      # save and login user
      user.save()
      login(request, user)

      return redirect('home')
    else:
      messages.error(request, 'An error occurred during registration.')

  ctx = {'form': form}
  return render(request, 'base/login_register.html', ctx)

@login_required(login_url='login')
def delete_msg(request, id):
  msg = Message.objects.get(id=id)

  if request.user != msg.user:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    msg.delete()
    return redirect('home')
  
  ctx = {
    'obj': msg
  }
  return render(request, 'base/delete.html', ctx)

@login_required(login_url='login')
def edit_msg(request, id):
  msg = Message.objects.get(id=id)
  if request.method == 'POST':
    msg.content = request.POST.get('content')

    # if the user leaves the content blank, ask them if they want to delete
    if not msg.content:
      return delete_msg(request, id)
    
    msg.save()
    return redirect('room', id=msg.room.id)
  
  ctx = {
    'obj': msg
  }
  return render(request, 'base/edit.html', ctx)


def user_profile(request, id):
  user = User.objects.get(id=id)
  rooms = user.room_set.all()
  msgs = user.message_set.all()
  topics = Topic.objects.all()

  ctx = {
    'user': user,
    'rooms': rooms,
    'msgs': msgs,
    'topics': topics
  }
  return render(request, 'base/profile.html', ctx)

@login_required(login_url='login')
def update_user(request):
  user = request.user
  form = UserForm(instance=user)

  if request.method == 'POST':
    form = UserForm(request.POST, instance=user)
    if form.is_valid():
      form.save()
      return redirect('user-profile', id=user.id)

  ctx = {'form': form}
  return render(request, 'base/update_user.html', ctx)
