from django.urls import path
from . import views


app_name = 'instagram_profile'

urlpatterns = [
    path('', views.feed, name='feed'),
]
