from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('_payment_intent/', views.create_payment, name='create_payment'),
]