from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart, name='cart'),
    path('add/<model_name>&<game_id>', views.cart_add, name='cart_add'),
]