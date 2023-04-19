from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about_page, name='about'),
    path('support/', views.support_page, name='support'),
    path('media/', views.media, name='media'),
    path('media/add/', views.media_add, name='media_add'),
    path('media/<media_id>/edit/', views.media_edit, name='media_edit'),
    path('media/<media_id>/delete/', views.media_delete, name='media_delete'),
]