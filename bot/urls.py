from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'bot'

urlpatterns = [
    # path('', views.index, name= 'index'),
    path('event/', views.event, name= 'event_handler'),
]

