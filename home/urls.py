from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('media/', views.media, name='media'),
    path('media/add/', views.media_add, name='media_add'),
]