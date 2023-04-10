from django.urls import path
from . import views

urlpatterns = [
    path('', views.myprofile, name='profile'),
    path('billing/', views.billing_address, name='billing_address')
]