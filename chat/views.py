from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Profile


def home(request):
    return render(request, 'chat/home.html')

def room(request, room_name):
    username = request.GET.get('username', 'Guest')
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': username
    })


def join_room(request):
    username = request.POST.get('username')
    room_name = request.POST.get('room_name')
    return redirect(f'/chat/{room_name}/?username={username}')

