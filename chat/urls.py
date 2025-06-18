from django.urls import path
from . import views 
from .views import get_previous_messages


urlpatterns = [
    path('', views.home, name='home'),
    path('join/', views.join_room, name='join_room'),
    path('<str:room_name>/', views.room, name='room'),
    path('messages/<str:room_name>/', get_previous_messages, name='get_previous_messages'),
]  