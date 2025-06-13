from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('join/', views.join_room, name='join_room'),
    path('<str:room_name>/', views.room, name='room'),

]  