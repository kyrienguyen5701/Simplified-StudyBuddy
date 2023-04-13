from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
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
  msgs = room.message_set.all().order_by('-created')
  participants = room.participants.all()

  if request.method == 'POST':
    msg = Message.objects.create(
      user=request.user,
      room=room,
      body=request.POST.get('body')
    )

    # add a new user once they comment
    room.participants.add(request.user)

    return redirect('room', id=room.id)
  
  ctx = {'room': room, 'msgs': msgs, 'participants': participants}
  return render(request, 'base/room.html', ctx)

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def delete_room(request, id):
  room = Room.objects.get(id=id)

  if request.method == 'POST':
    room.delete()
    return redirect('home')
  
  return render(request, 'base/delete.html', {'obj': room})

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
  if request.method == 'POST':
    msg.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': msg})

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
  return render(request, 'base/edit.html', {'obj': msg})
