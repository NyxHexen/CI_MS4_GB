from django.urls import path
from . import views

urlpatterns = [
    path('<promo_id>', views.promo, name='promo'),
    path('add/', views.promo_add, name='promo_add')
]