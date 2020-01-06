from django.urls import path
from . import views


app_name = 'instagram'

urlpatterns = [
    path('', views.feed, name='feed'),
]
