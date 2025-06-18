from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Profile, Message
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from .serializers import MessageSerializer 

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


@api_view(['GET'])
def get_previous_messages(request, room_name):
    messages = Message.objects.filter(room=room_name).order_by('-timestamp')[:25]
    messages = reversed(messages)  
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)